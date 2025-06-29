# smart_pdf_renamer
Use AI (Azure OpenAI) to look at the pdf content and rename the file accordingly

This has only been tested on windows. 

he program expects the follwoing environment variables to be defined: 
AZURE_GPT_KEY           = os.getenv("AZURE_GPT4O_KEY")    #(deployment name) Example: 2348feh787hf38734843hf8743h743h (not a real key)
AZURE_GPT_EP            = os.getenv("AZURE_GPT4O_EP")     #(endpoint) Example: https://something.openai.azure.com/
AZURE_GPT_DEPLOY        = os.getenv("AZURE_GPT4O_DEP")    #(deployment name) Example: my-gpt-4o-dep
AZURE_GPT_VER           = os.getenv("AZURE_GPT4O_VER")    #(api_version) Example: 2024-05-01-preview
AZURE_GPT_MODEL         = os.getenv("AZURE_GPT4O_MODEL")  #(model name) Example: gpt-4o
