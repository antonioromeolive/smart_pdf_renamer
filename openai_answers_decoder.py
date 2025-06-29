#below a typical response from OpenAI API. try to encapsulate... not sure if this answer contains all fields....
"""
{
  "id": "chatcmpl-8jOoVLNTzbAOW4AxYEkTUSNwn4I2u",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "TEST OK 74\n\nConversation Length: 1 message\nToken Count: 1 token\nNumber of Words: 1 word",
        "role": "assistant",
        "function_call": null,
        "tool_calls": null
      }
    }
  ],
  "created": 1705830835,
  "model": "gpt-4",
  "object": "chat.completion",
  "system_fingerprint": "fp_6d044fb900",
  "usage": {
    "completion_tokens": 26,
    "prompt_tokens": 188,
    "total_tokens": 214
  }
}


payload = {
    "messages": [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are an AI assistant that helps people find information."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                },
                {
                    "type": "text",
                    "text": "describe the image"
                }
            ]
        },
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800
}

"""

def get_temperature(data):
    return data.get('temperature')

def get_top_p(data):
    return data.get('top_p')

def get_max_tokens(data):
    return data.get('max_tokens')

def get_message_content_type(data):
    return data['choices'][0]['message']['content'][0].get('type') if data.get('choices') and data['choices'][0].get('message') else None

def get_message_content_text(data):
    #return data['choices'][0]['message']['content']
    return data['choices'][0]['message']['content'][0].get('text') if data.get('choices') and data['choices'][0].get('message') else None

def get_message_content_image_url(data):
    return data['choices'][0]['message']['content'][0]['image_url'].get('url') if data.get('choices') and data['choices'][0].get('message') else None

def get_id(data):
    return data.get('id')

def get_choices(data):
    return data.get('choices')

def get_finish_reason(data):
    return data['choices'][0].get('finish_reason') if data.get('choices') else None

def get_index(data):
    return data['choices'][0].get('index') if data.get('choices') else None

def get_logprobs(data):
    return data['choices'][0].get('logprobs') if data.get('choices') else None

def get_message(data):
    return data['choices'][0].get('message') if data.get('choices') else None

def get_answer(data) -> str:
    """ This is just the same as get_content so far """
    return get_content(data)

def get_content(data)->str:
    """ return the actual answer from a Azure OpenAI query """
    return data['choices'][0]['message'].get('content') if data.get('choices') and data['choices'][0].get('message') else None

def get_role(data):
    return data['choices'][0]['message'].get('role') if data.get('choices') and data['choices'][0].get('message') else None

def get_function_call(data):
    return data['choices'][0]['message'].get('function_call') if data.get('choices') and data['choices'][0].get('message') else None

def get_tool_calls(data):
    return data['choices'][0]['message'].get('tool_calls') if data.get('choices') and data['choices'][0].get('message') else None

def get_created(data):
    return data.get('created')

def get_model(data):
    return data.get('model')

def get_object(data):
    return data.get('object')

def get_system_fingerprint(data):
    return data.get('system_fingerprint')

def get_usage(data):
    return data.get('usage')

def get_completion_tokens(data):
    return data['usage'].get('completion_tokens') if data.get('usage') else None

def get_prompt_tokens(data):
    return data['usage'].get('prompt_tokens') if data.get('usage') else None

def get_total_tokens(data):
    return data['usage'].get('total_tokens') if data.get('usage') else None
"""
def get_response_tokens(data) ->int:
    return data['usage']['completion_tokens']

def get_total_tokens(data) ->int:
    return data['usage']['total_tokens']

"""

if __name__ == '__main__':
    print("OpenAI Answers Decoder - not an executable module.")