from openai import AsyncOpenAI

from backend.app.core.schema_loader import FeatureSchema
from backend.app.core.prompt_builder import PromptBuilder
from backend.app.schemas.extraction import ExtractionResult
from backend.app.services.safeguard import SafeguardService


class ExtractionError(Exception):
    """Raised when extraction fails due to safeguard, refusal, or API issues."""

    def __init__(self, message: str, safeguard_triggered: bool = False):
        super().__init__(message)
        self.safeguard_triggered = safeguard_triggered


class ExtractionService:
    """Extracts clinical variables from free-text using OpenAI structured outputs.

    Uses GPT-4o-mini with Pydantic ExtractionResult as response_format.
    Integrates SafeguardService for pre-input and post-output checking.
    """

    MODEL = "gpt-4o-mini"
    TEMPERATURE = 0
    MAX_TOKENS = 1000

    def __init__(
        self,
        schema: FeatureSchema,
        openai_client: AsyncOpenAI,
        safeguard: SafeguardService,
    ):
        self.schema = schema
        self.client = openai_client
        self.safeguard = safeguard
        self.system_prompt = PromptBuilder.build_system_prompt(schema)

    async def extract(self, user_input: str) -> ExtractionResult:
        """Extract clinical variables from clinician's free-text input.

        Args:
            user_input: Raw clinician text describing a patient case.

        Returns:
            ExtractionResult with extracted features (null for unmentioned fields).

        Raises:
            ExtractionError: If input fails safeguard check, model refuses, or
                LLM produces blocked content.
        """
        # Step 1: Pre-LLM input guard (SAFE-02)
        input_check = self.safeguard.check_input(user_input)
        if not input_check.safe:
            raise ExtractionError(input_check.message, safeguard_triggered=True)

        # Step 2: Build messages with XML tag wrapping (D-09)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": PromptBuilder.build_user_message(user_input)},
        ]

        # Step 3: Call OpenAI with structured output (D-01, SAFE-04)
        # SDK has built-in retry for 429/5xx (D-18)
        response = await self.client.beta.chat.completions.parse(
            model=self.MODEL,
            messages=messages,
            response_format=ExtractionResult,
            temperature=self.TEMPERATURE,
            max_tokens=self.MAX_TOKENS,
        )

        # Step 3b: Check for model refusal (D-19)
        if response.choices[0].message.refusal:
            raise ExtractionError(
                f"Model refused extraction: {response.choices[0].message.refusal}",
                safeguard_triggered=False,
            )

        result: ExtractionResult = response.choices[0].message.parsed

        # Step 4: Post-generation output scan (SAFE-03)
        raw_content = response.choices[0].message.content or ""
        output_check = self.safeguard.check_output(raw_content)
        if not output_check.safe:
            raise ExtractionError(output_check.message, safeguard_triggered=True)

        return result
