"""Basic usage examples for auto-structured-output package"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from auto_structured_output import StructureExtractor

# Initialize OpenAI client
load_dotenv(".envrc")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the structure extractor
extractor = StructureExtractor(client)


def run(prompt: str, file_name: str):
    T_Model = extractor.extract_structure(prompt)

    print(f"Generated model: {T_Model.__name__}")
    print(f"Fields: {T_Model.model_json_schema()}")

    # Use the model
    response = client.chat.completions.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format=T_Model,
    )

    data = response.choices[0].message.parsed
    data_dict = data.model_dump()
    print("\nGenerated data:")
    print(data_dict)

    extractor.save_extracted_json(T_Model, file_name)


def example_1_simple_user_model():
    """Example 1: Extract a simple user model"""
    print("\n=== Example 1: Simple User Model ===")

    prompt = """
We have collected the user’s profile information as follows.

<example>
John Doe
21 years old
johndoe@example.com
Male
Tokyo, Japan
Theme: light
No notifications
</example>

Please output the user information in the following format:
- User's name
- Age
- Email address
- Preferences
  - Theme ("light" or "dark"; default "light")
  - Whether notifications are enabled

    """

    run(prompt, "schemas/simple_user_model.json")


def example_2_product_with_enum():
    """Example 2: Product model with enum status"""
    print("\n=== Example 2: Product with Enum Status ===")

    prompt = """We have the following product information.
<product>
ID: P12345
Name: Wireless Mouse
Price: 29.99
Status: available
</product>

Please output the product information in the following format:
- product_id
- name
- price: Product price (must be 0 or greater)
- status: one of "available", "out_of_stock", "discontinued"
    """

    run(prompt, "schemas/product_with_enum.json")


def example_3_optional_fields():
    """Example 3: Model with optional fields"""
    print("\n=== Example 3: Optional Fields ===")

    prompt = """Analyze the following book information.
<book>
Title: The Great Gatsby
Author: F. Scott Fitzgerald
ISBN: 9780743273565
Publication Year: 1925
Rating: 4.2
Comments: A classic novel of the Jazz Age.
Reviews: 3500
</book>
    
Please output the book information in the following format:
- title (string, required): Book title
- author (string, required): Author name
- isbn (string, optional): ISBN number
- publication_year (integer, optional): Year published
- rating (number, optional): Rating from 0 to 5
    """

    run(prompt, "schemas/book_with_optional_fields.json")


def example_4_array_fields():
    """Example 4: Model with array fields"""
    print("\n=== Example 4: Array Fields ===")

    prompt = """Review the following course information.
<course>
Course ID: CS101
Title: Introduction to Computer Science
Instructor: Dr. Smith
Topics: Programming, Algorithms, Data Structures
Prerequisites: None
</course>
    
Please output the course information in the following format:
course_id
title
instructor
topics
prerequisites
    """

    run(prompt, "schemas/course_with_array_fields.json")


def example_5_datetime_fields():
    """Example 5: Model with date-time fields"""
    print("\n=== Example 5: DateTime Fields ===")

    prompt = """You are an expert event organizer.
Here is the event information:
<event>
Event ID: E56789
Name: Tech Conference 2024
Start Time: 2024-09-15T09:00:00Z
End Time: 2024-09-15T17:00:00Z
Location: San Francisco, CA
</event>

Please output the event information in the following format:
- event_id
- name
- start_time
- end_time
- location
    """

    run(prompt, "schemas/event_with_datetime_fields.json")


if __name__ == "__main__":
    print("Auto-Structured-Output: Basic Usage Examples")
    print("=" * 50)

    example_1_simple_user_model()
    example_2_product_with_enum()
    example_3_optional_fields()
    example_4_array_fields()
    example_5_datetime_fields()

    print("\n" + "=" * 50)
    print("All examples completed successfully!")
