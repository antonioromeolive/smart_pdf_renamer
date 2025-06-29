# smart_pdf_renamer
Use AI (Azure OpenAI) to look at the pdf content and rename the file accordingly

This has only been tested on Windows.

The program expects the following environment variables to be defined:

- `AZURE_GPT_KEY`  
  (Example: `2348feh787hf38734843hf8743h743h`)  
  *(not a real key)*

- `AZURE_GPT_EP`  
  (Example: `https://something.openai.azure.com/`)

- `AZURE_GPT_DEPLOY`  
  (Example: `my-gpt-4o-dep`)

- `AZURE_GPT_VER`  
  (Example: `2024-05-01-preview`)

- `AZURE_GPT_MODEL`  
  (Example: `gpt-4o`)
