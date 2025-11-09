# AI Integration Requirements Definition

This document outlines the detailed requirements for integrating real AI models into the chart-craft-ai application for YAML generation.

## 1. Authentication and API Key Management

- **Secure Storage:** API keys for AI services (e.g., OpenAI, Google AI) must be stored securely and not be hardcoded in the source code.
- **Configuration:** The application will use environment variables to configure the API keys. This aligns with the existing configuration management using Pydantic's `BaseSettings`.
- **Access Control:** The backend service will be responsible for accessing the API keys and making requests to the AI services. The keys should not be exposed to the frontend or any client-side code.

## 2. Configuration

- **Model Selection:** The application will support multiple AI models. The `generator_name` parameter in the API will be used to select the desired model (e.g., "openai_gpt4_turbo", "google_gemini_pro_vision").
- **Generator Configuration:** Each generator will have its own configuration for model-specific parameters (e.g., temperature, max_tokens, top_p). These configurations will be managed within the backend.
- **Feature Flags:** The AI-powered generation can be enabled or disabled via an environment variable. This will allow for running the application without AI features if needed.

## 3. Text-to-YAML Generation (LLM)

- **Provider:** Initially, we will support OpenAI's GPT models (e.g., GPT-4, GPT-3.5-turbo). The architecture should be flexible enough to add other providers in the future.
- **API Integration:**
    - A new class, `TextToYamlOpenAIGenerator`, will be created, implementing the `YamlGenerator` interface.
    - This class will use the `openai` Python client library to interact with the OpenAI API.
- **Prompt Engineering:**
    - A system prompt will be designed to instruct the LLM on its role as a circuit design assistant.
    - The user's prompt will be embedded in a larger prompt structure that includes:
        - The system prompt.
        - The desired YAML schema/format description (from `circuit_yaml_spec.md`).
        - Few-shot examples of valid circuit YAML.
        - The user's request.
- **Output Parsing and Validation:**
    - The generator will expect the LLM to return the YAML content within a specific format (e.g., a code block).
    - The extracted YAML will be parsed and validated. The existing circuit rendering and validation logic can be reused for this purpose.
- **Error Handling:**
    - The generator will handle API errors from the LLM provider (e.g., authentication errors, rate limits).
    - It will also handle cases where the LLM's response is not in the expected format or the generated YAML is invalid.

## 4. Image-to-YAML Generation (Vision Model)

- **Provider:** We will start with a model that supports vision, such as OpenAI's GPT-4 with Vision or Google's Gemini Pro Vision.
- **API Integration:**
    - A new class, `ImageToYamlVisionGenerator`, will be updated to call the real vision model API.
    - The image data will be base64-encoded and sent to the API as part of the request payload.
- **Prompt Engineering:**
    - The prompt will instruct the model to analyze the image of a circuit diagram and generate the corresponding YAML representation.
    - The prompt will include the same YAML schema description and examples as the text-based generator.
- **Output Parsing and Validation:**
    - The process will be similar to the text-to-YAML generator. The YAML will be extracted from the model's response, parsed, and validated.
- **Error Handling:**
    - The generator will handle API errors and cases where the model fails to interpret the image or generates invalid YAML.

## 5. Implementation Plan

1.  **API Key Management:** Add the necessary environment variables and update the configuration (`app/core/config.py`) to load the AI service API keys.
2.  **Text-to-YAML Generator:**
    - Implement `TextToYamlOpenAIGenerator`.
    - Develop the prompt templates.
    - Update the `GeneratorFactory` to include the new generator.
    - Add unit tests for the new generator, mocking the AI service API calls.
3.  **Image-to-YAML Generator:**
    - Update the existing `ImageToYamlVisionGenerator` to call a real vision model API.
    - Develop the prompt templates for image analysis.
    - Update the `GeneratorFactory` if necessary.
    - Add/update unit tests for the vision generator.
4.  **API Endpoint Integration:** The existing `/generate-and-render` endpoint is already designed to work with the factory. No major changes are expected here, but it will need to be tested with the real generators.
5.  **Frontend Integration:** The frontend already supports calling the `/generate-and-render` endpoint. The UI might need adjustments to allow users to select the generator/model.
