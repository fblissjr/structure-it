"""Example: Extract structured recipe data from unstructured text.

This example demonstrates the basic usage of structure-it for extracting
structured data using the Gemini API and Pydantic schemas.

Usage:
    uv run python examples/extract_recipe.py
"""

import asyncio
import os

from structure_it.extractors import GeminiExtractor
from structure_it.schemas import BaseSchema


class Recipe(BaseSchema):
    """Schema for structured recipe data."""

    name: str
    description: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    servings: int | None = None
    ingredients: list[str]
    instructions: list[str]
    tags: list[str] = []


SAMPLE_RECIPE = """
Classic Chocolate Chip Cookies

These homemade chocolate chip cookies are soft, chewy, and packed with
chocolate chips. Perfect for any occasion!

Time: 15 minutes prep, 12 minutes baking
Makes about 24 cookies

What you need:
- 2 1/4 cups all-purpose flour
- 1 tsp baking soda
- 1 tsp salt
- 1 cup butter, softened
- 3/4 cup granulated sugar
- 3/4 cup packed brown sugar
- 2 large eggs
- 2 tsp vanilla extract
- 2 cups chocolate chips

How to make:
1. Preheat your oven to 375°F (190°C).
2. Mix flour, baking soda, and salt in a bowl.
3. In a separate large bowl, beat butter and both sugars until creamy.
4. Add eggs and vanilla to the butter mixture and beat well.
5. Gradually stir in the flour mixture.
6. Fold in the chocolate chips.
7. Drop rounded tablespoons of dough onto ungreased cookie sheets.
8. Bake for 10-12 minutes or until golden brown.
9. Let cool on baking sheet for 2 minutes, then transfer to a wire rack.
"""


async def main() -> None:
    """Run the recipe extraction example."""
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        return

    print("=" * 80)
    print("Recipe Extraction Example")
    print("=" * 80)
    print()

    # Initialize the extractor with the Recipe schema
    # Uses default model from config (can override via STRUCTURE_IT_MODEL env var)
    extractor = GeminiExtractor(schema=Recipe)

    print("Input Text:")
    print("-" * 80)
    print(SAMPLE_RECIPE)
    print()

    # Extract structured recipe data
    print("Extracting structured recipe data...")
    print()

    try:
        recipe = await extractor.extract(
            content=SAMPLE_RECIPE,
            prompt=(
                "Extract the recipe information from the text. "
                "Parse ingredients and instructions as separate list items. "
                "Infer appropriate tags based on the recipe content."
            ),
        )

        print("Extracted Recipe:")
        print("-" * 80)
        print(recipe.to_json())
        print()

        print("=" * 80)
        print("Success! Recipe data extracted and structured.")
        print("=" * 80)

    except Exception as e:
        print(f"Error during extraction: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
