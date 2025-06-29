# Author:  Antonio Romeo
# Date:    2024-05-12
# This file contains code for performing Optical Character Recognition (OCR) on images.
# It uses the Azure OpenAI model to extract text from images and writes the extracted text to an output file.
# MIT License (read full license terms at the end of this file or in LICENSE.TXT file)

import base64
import json
import tiktoken
from rom_print import COLOR_YELLOW, COLOR_CYAN, COLOR_LIGHT_GREEN, COLOR_GRAY, COLOR_WHITE, printColor, printTwoColors

AIC_TYPE_TEXT        = "text"        #text message
AIC_TYPE_IMAGE_URL   = "image_url"   #image URL message
AIC_TYPE_FILE        = "file"        #not implemented yet
AIC_TYPE_UNKNOWN     = "unknown"     #not implemented yet
AIC_TYPE_INTERNAL    = "internal"    #not implemented yet

AIC_ROLE_USER        = "user"        #user message
AIC_ROLE_SYSTEM      = "system"      #system message
AIC_ROLE_ASSISTANT   = "assistant"   #assistant message
AIC_ROLE_UNKNOWN     = "unknown"     #unknown message
AIC_ROLE_DEVELOPER   = "developer"   #developer message
AIC_ROLE_INTERNAL    = "internal"    #message with ROLE INTERNAL will never be sent to AI model and will not count in any sizing, history size etc....

AIC_DEFAULT_SYSTEM_PROMPT       = "You are an AI assistant trying to be useful"
AIC_DEFAULT_MEMORY_SIZE         = 8192
AIC_MODEL_NAME_FOR_TOKEN_COUNT  = "gpt-4o"

AIC_COMMAND_NEWTOPIC = "newtopic"

class AIMessageContent:
    """ This class represents the content of a message. It can be a text message or an image message.
    """
    def __init__(self, msg_type: str, msg_image_url: str = "", msg_text: str = "") -> None:
        self.__content:  list[dict[str, str]] = []
        self.__type: str = msg_type
        self.__image_url: str = msg_image_url
        self.__text: str = msg_text
        self.set_content(msg_type, msg_image_url, msg_text)


    def to_dict(self)-> dict[str, str]:
        my_dict_version: dict[str, str] = {
            'type': self.__type,
            'image_url': self.__image_url,
            'text': self.__text
        }
        return my_dict_version
    
    @classmethod
    def from_dict(cls, d):
        return cls(d['type'], d['image_url'], d['text'])
    
    def get_type(self) -> str:
        return self.__type
    
    def get_image_url(self) -> str:
        return self.__image_url
    
    def get_text(self) -> str:
        return self.__text
    
    def get_content(self) -> list[dict[str, str]]:
        return self.__content
    
    def set_content(self, msg_type: str, msg_image_url: str = "", msg_text: str = "") -> None:
        self.__type: str = msg_type
        self.__image_url: str = msg_image_url
        self.__text: str = msg_text

        if msg_type == AIC_TYPE_IMAGE_URL:
            if msg_image_url.startswith("http"):
                self.__content = [
                    {
                        "type": AIC_TYPE_IMAGE_URL,
                        "image_url": {
                            "url": msg_image_url
                        }
                    },
                    {
                        "type": AIC_TYPE_TEXT,
                        "text": msg_text
                    }
                ]
            elif msg_image_url.startswith("data:image"):
                self.__content = [
                    {
                        "type": AIC_TYPE_IMAGE_URL,
                        "image_url": {
                            "url": msg_image_url
                        }
                    },
                    {
                        "type": AIC_TYPE_TEXT,
                        "text": msg_text
                    }
                ]
            else:
                try:
                    with open(msg_image_url, "rb") as image_file:
                        encoded_image: str = base64.b64encode(image_file.read()).decode("utf-8")
                    self.__image_url = f"data:image/jpeg;base64,{encoded_image}"
                    self.__content = [
                        {
                            "type": AIC_TYPE_IMAGE_URL,
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        },
                        {
                            "type": AIC_TYPE_TEXT,
                            "text": msg_text
                        }
                    ]
                except OSError as e:
                    print("Error opening image file:", e)
                    self.__content = [
                        {
                            "type": AIC_TYPE_IMAGE_URL,
                            "image_url": {
                                "url": f"Error opening image file: {msg_image_url}"
                            }
                        },
                        {
                            "type": AIC_TYPE_TEXT,
                            "text": msg_text
                        }
                    ]

                
        elif msg_type == AIC_TYPE_TEXT:
            self.__content = [
                {
                    "type": AIC_TYPE_TEXT,
                    "text": msg_text
                }
            ]
        elif msg_type == AIC_TYPE_FILE: #for future usages
            self.__content = [
                {
                    "type": AIC_TYPE_FILE,
                    "text": "This format is not supported yet"
                }
            ]
        elif msg_type == AIC_TYPE_INTERNAL: #store a command, internal message... will be not sent to AI
            self.__content = [
                {
                    "type": AIC_TYPE_INTERNAL,
                    "text": msg_text
                }
            ]            
        else:
            raise ValueError("Invalid message type: " + msg_type)
        
        
    def to_string(self) -> str:
        result:str= ""
        if self.__type == AIC_TYPE_IMAGE_URL:
            result = f"Image URL: {self.__image_url}\nText: {self.__text}"
            self.__content[0]["image_url"]["url"] = self.__image_url
        elif self.__type == AIC_TYPE_FILE:
            result = f"File  URL: {self.__image_url}\nText: {self.__text}"
        elif self.__type == AIC_TYPE_TEXT:
            result = f"Text: {self.__text}"
        elif self.__type == AIC_TYPE_INTERNAL:
            result = f"Text: {self.__text}"
        return result


class AIMessage:
    def __init__(self, role: str, content_text:str, msg_type:str, content_image_url:str = None, sticky:bool = False) -> None: 
        """ This a message to or from AI assistant. It can be a text message or an image message.
        Args:   role: str - the role of the message. It can be "User" or "System" or "Assistant" - MUST NOT be None
                msg_type - the type of the message. It can be "text" or "image_url" - MUST NOT be None
                content_text: str - the text of the message - MUST NOT be None
                content_image_url: str - the url of the image to be sent. if not None the message contains a link to an image
                sticky: bool - if the message is sticky or not
                NOTE: once built you can change the content_text, content_image_url and sticky flag using the appropriate methods below
                but it requires you to pass an AIMessageContent object to the set_content method.
                the get_message_payload() method can be used to build a conversation string to be passed to (Azure) OpenAI
        """
        self.__role: str = role
        self.__content:AIMessageContent = None
        self.__sticky: bool = sticky
        self.__estimated_tokens: int = 0
        self.__is_internal: bool = False

        if (role not in [AIC_ROLE_USER, AIC_ROLE_ASSISTANT, AIC_ROLE_SYSTEM, AIC_ROLE_DEVELOPER, AIC_ROLE_INTERNAL]):
            raise ValueError("Invalid message role: " + role)

        if (msg_type == AIC_TYPE_IMAGE_URL):
            if content_image_url is None or content_image_url == "":
                raise ValueError("Missing Image URL for " + msg_type + " message")
            else:
                self.__content = AIMessageContent(AIC_TYPE_IMAGE_URL, content_image_url, content_text)
                self.__estimated_tokens = self.num_tokens_from_picture(content_image_url) + self.num_tokens_from_string(content_text)
        elif (msg_type == AIC_TYPE_INTERNAL):
            if content_text is None or content_text == "":
                raise ValueError("Missing TEXT for " + msg_type + " message")
            self.__content = AIMessageContent(AIC_TYPE_INTERNAL, None, content_text)
            self.__is_internal = True
            self.__estimated_tokens = 0 #internal messages are not sent to AI so no token no cry
        elif (msg_type == AIC_TYPE_TEXT):
            if content_text is None or content_text == "":
                raise ValueError("Missing TEXT for " + msg_type + " message")
            self.__content = AIMessageContent(AIC_TYPE_TEXT, None, content_text)
            self.__estimated_tokens = self.num_tokens_from_string(content_text)
        elif (msg_type == AIC_TYPE_FILE):
            raise ValueError("Unsupported (yet) message type: " + msg_type)
        else:
            raise ValueError("Invalid message type: " + msg_type)
        
    def num_tokens_from_picture(self, encoded_image:str) -> int:
        """ I need to understand better the way to calculate this... 
            in the meanwhile this is the expected tokens of a 1024x1024 image 
        """
        #todo: TO BE IMPLEMENTED
        num_tokens:int = 765 
        return num_tokens

    def num_tokens_from_string(self, the_string: str, model_name: str = AIC_MODEL_NAME_FOR_TOKEN_COUNT) -> int:
        """return num of tokens from a string... model name sample: gpt-4 """
        encoding = tiktoken.encoding_for_model(model_name)
        num_tokens: int = len(encoding.encode(the_string))
        return num_tokens

    def get_estimated_tokens(self) -> int:
        return self.__estimated_tokens
    
    def to_dict(self) -> dict[str, str]:
        my_dict_version: dict[str, str] = {
            'role': self.__role,
            'msg_type': self.__content.get_type(),
            'content_text': self.__content.get_text(),
            'content_image_url': self.__content.get_image_url(),
            'sticky': self.__sticky
        }
        return my_dict_version
    
    def to_string(self) -> str:
        result:str= f"Role: {self.__role}\nContent: {self.__content.to_string()}\nSticky: {self.__sticky}"
        return result


    @classmethod
    def from_dict(cls, d):
        return cls(d['role'], d['msg_type'], d['content_text'], d['content_image_url'], d['sticky'])
    
    def get_type(self) -> str:
        return self.__content.get_type()
    
    def get_url(self) -> str:
        return self.__content.get_image_url()
    
    def get_text(self) -> str:
        return self.__content.get_text()
    
    def get_role(self) -> str:
        return self.__role

    def set_role(self, role: str) -> None:
        self.__role = role

    def set_sticky(self, sticky: bool) -> None:
        """ Sticky messages are not removed from the conversation memory when a new message is added. 
            They are kept in the conversation until the user decides to remove them. 
            However there is a flag in the removemessages method to remove sticky messages as well.
        """
        self.__sticky = sticky

    def is_sticky(self) -> bool:
        return self.__sticky

    def is_internal(self) -> bool:
        return self.__is_internal

    def set_content(self, content: AIMessageContent) -> None:
        self.__content: AIMessageContent = content

    def get_content(self) -> AIMessageContent:
        return self.__content

    def get_message_payload(self) -> dict:
        payload = {
            "role": self.get_role(),
            #"sticky": self.is_sticky(),
            "content": self.get_content().get_content()
        }
        return payload


class AIConversation:
    def __init__(self, system_message:str = None,  max_memory:int = AIC_DEFAULT_MEMORY_SIZE) -> list[AIMessage]:
        """ This class represents a conversation between a user and an AI assistant.
            Careless of the length of the conversation only "max_memory" messages will be used from the get_conversation_payload() method.
            Extra messages will be ignored...
        """
        self.__messages: list[AIMessage] = None
        self.__memory_messages: list[AIMessage] = None

        self.__max_memory_messages: int     = max_memory #the maximum number of messages to be used in the conversation with AI (NOT including the system message)

        self.__system_message_tokens: int   = 0          #tokens used by the system message

        self.__user_tokens: int             = 0          #tokens used by the user messages (whole history)
        self.__assistant_tokens: int        = 0          #tokens used by the assistant messages (whole history)
        self.__total_tokens: int            = 0          #the total number of tokens in the conversation. calculated automatically at every insert/remove
        self.__biggest_user_msg_tokens: int         = 0          
        self.__biggest_assistant_msg_tokens: int    = 0          
        
        self.__memory_user_tokens: int      = 0          #the total number of tokens in the conversation memory (i.e. limited to the last __maxmero). calculated automatically at every insert/remove
        self.__memory_assistant_tokens: int = 0          #the total number of tokens in the conversation. calculated automatically at every insert/remove
        self.__memory_total_tokens: int     = 0          #the total number of tokens in the conversation. calculated automatically at every insert/remove

        the_system_msg:str = ""

        #enforce rules for messages in the conversation:
        #1 there can be only 1 system message at the beginning of the conversation
        if system_message is not None and len(system_message.strip()) > 0:
            the_system_msg = system_message.strip()
        else:
            the_system_msg = AIC_DEFAULT_SYSTEM_PROMPT
            #create a standard system message
        
        self.__messages = [AIMessage(AIC_ROLE_SYSTEM, the_system_msg, AIC_TYPE_TEXT, None, True)]
        
        self.__total_tokens = self.__messages[0].get_estimated_tokens()
        self.__system_message_tokens  = self.__total_tokens
        self.__memory_total_tokens    = self.__total_tokens

        self.__max_memory_messages = max_memory
        return


     
    @classmethod
    def from_file(cls, filename):
        # Create an instance of AIConversation starting from a file
        conversation = cls()

        # Load the conversation from the file
        conversation.load_conversation(filename)

        return conversation

    def get_biggest_user_msg_tokens(self) -> int:
        return self.__biggest_user_msg_tokens
    
    def get_biggest_assistant_msg_tokens(self) -> int:
        return self.__biggest_assistant_msg_tokens

    def get_system_tokens(self) -> int:
        return self.__system_message_tokens

    def get_memory_total_tokens(self) -> int:
        return self.__memory_total_tokens

    def get_total_tokens(self) -> int:
        return self.__total_tokens

    def get_memory_user_tokens(self) -> int:
        return self.__memory_user_tokens
    
    def get_memory_assistant_tokens(self) -> int:
        return self.__memory_assistant_tokens
    
    def get_user_tokens(self) -> int:
        return self.__user_tokens
    
    def get_assistant_tokens(self) -> int:
        return self.__assistant_tokens


    def load_conversation(self, full_path_name:str) -> None:
        i:int = 0
        self.__restart_internal()

        with open(full_path_name, "r", encoding="utf-8") as file:
            for line in file:
                message = json.loads(line.strip())
                try:
                    self.add_message(message["role"], message["content_text"], message["msg_type"], message["content_image_url"], message["sticky"])
                    i+=1
                except ValueError as e:
                    print(f"AIConversation.load_conversation() - Error loading message {i}: {e}")
                    print(f"Wrong Line {i}: {str(message)}")
                    continue
                except Exception as e:
                    raise e
        return  

    def save_conversation(self, full_path_name:str) -> None:
        with open(full_path_name, "w", encoding="utf-8") as file:
            for message in self.__messages:            
                file.write(json.dumps(message.to_dict()) + '\n')
        return

    def change_system_message(self, new_system_message: str) -> None:
        if len(self.__messages) == 0:
            self.__messages.append(AIMessage(AIC_ROLE_SYSTEM, new_system_message, AIC_TYPE_TEXT, None, True))
        else:
            self.__messages[0] = AIMessage(AIC_ROLE_SYSTEM, new_system_message, AIC_TYPE_TEXT, None, True)
        return

    def __restart_internal(self) -> None:
        """ Private method to allow removing all messages from the conversation INCLUDING the system message."""
        self.__messages = []
        self.__system_message_tokens = 0
        self.__user_tokens = 0
        self.__assistant_tokens = 0
        self.__total_tokens = 0
        self.__memory_user_tokens = 0
        self.__memory_assistant_tokens = 0
        self.__memory_total_tokens = 0
        self.__biggest_user_msg_tokens = 0          
        self.__biggest_assistant_msg_tokens = 0          

        return

    def new_topic(self) -> None:
        """ Add an internal AIC_COMMAND_NEWCONV message to the conversation. This will be used to signal a new topic in the conversation,
            i.e. "memory" will always start from here on
        """
        self.add_message(AIC_ROLE_INTERNAL, AIC_COMMAND_NEWTOPIC, AIC_TYPE_INTERNAL)
        return
    

    def add_message(self, msg_role:str, msg_text:str, msg_type:str=AIC_TYPE_TEXT, image_url:str = None, is_sticky = False) -> None:
        """ You cannot add a system message after the first message has been added to the conversation.
            You can add as many user and assistant messages as you want.
            A system message will replace the one at the beginning of the conversation.
            Raise an exception for unsupported message types
        """
        if msg_role not in [AIC_ROLE_USER, AIC_ROLE_ASSISTANT, AIC_ROLE_SYSTEM, AIC_ROLE_INTERNAL, AIC_ROLE_DEVELOPER]:
            raise ValueError("Invalid message role: " + msg_role)

        l_tokenstoremove:int = 0 
        
        try:
            new_msg = AIMessage(msg_role, msg_text, msg_type, image_url, is_sticky)
        except Exception as e:
            raise e
        #new_msg = AIMessage(msg_role, msg_text, msg_type, image_url, is_sticky)

        if msg_role in [AIC_ROLE_SYSTEM, AIC_ROLE_DEVELOPER]:
            if len(self.__messages) >= 1:
                l_tokenstoremove = self.__messages[0].get_estimated_tokens()
                self.__messages[0] = new_msg
            else:
                self.__messages.append(new_msg)
        elif (len(self.__messages) > self.__max_memory_messages+2) and msg_role not in [AIC_ROLE_INTERNAL]:  #I am addind a non-system_message. I need to remove the oldest one from "memory" calculation
            l_tokenstoremove = self.__messages[-self.__max_memory_messages-1].get_estimated_tokens()
        
        if msg_role in [AIC_ROLE_USER, AIC_ROLE_ASSISTANT, AIC_ROLE_INTERNAL]:
            self.__messages.append(new_msg)

        l_msg_tokens:int     = new_msg.get_estimated_tokens()
   
        if msg_role == AIC_ROLE_USER:
            self.__user_tokens += l_msg_tokens - l_tokenstoremove
            self.__total_tokens += l_msg_tokens
            self.__memory_user_tokens += l_msg_tokens
            self.__memory_total_tokens += l_msg_tokens
            self.__memory_user_tokens -= l_tokenstoremove
            self.__memory_total_tokens -= l_tokenstoremove
            if l_msg_tokens > self.__biggest_user_msg_tokens:
                self.__biggest_user_msg_tokens = l_msg_tokens
        elif msg_role == AIC_ROLE_ASSISTANT:
            self.__assistant_tokens += l_msg_tokens - l_tokenstoremove
            self.__total_tokens += l_msg_tokens
            self.__memory_assistant_tokens += l_msg_tokens
            self.__memory_total_tokens += l_msg_tokens
            self.__memory_assistant_tokens -= l_tokenstoremove
            self.__memory_total_tokens -= l_tokenstoremove
            if l_msg_tokens > self.__biggest_assistant_msg_tokens:
                self.__biggest_assistant_msg_tokens = l_msg_tokens
        elif msg_role == AIC_ROLE_SYSTEM:
            self.__system_message_tokens = l_msg_tokens
            self.__total_tokens += l_msg_tokens
            self.__memory_total_tokens += l_msg_tokens
            self.__total_tokens -= l_tokenstoremove
            self.__memory_total_tokens -= l_tokenstoremove
        elif msg_role == AIC_ROLE_INTERNAL:
            pass #internal messages are not counted in tokens

        return
    
    def get_memory_messages(self) -> list[AIMessage]:
        """
        Retrieve the list of messages that are part of the conversation memory.

        This method returns a subset of the conversation messages that fit within the memory limit (`__max_memory_messages`).
        It includes sticky messages and handles special cases, such as detecting a new topic.

        The function works as follows:
        - Iterates through the messages in reverse order (starting from the most recent).
        - Adds messages to the memory list until the memory limit is reached.
        - Includes sticky messages even if they exceed the memory limit.
        - Stops adding messages if a "new topic" internal message (`AIC_COMMAND_NEWTOPIC`) is encountered.
        - Ensures the system message (first message in the conversation) is included if a new topic is found.

        Returns:
            list[AIMessage]: A list of `AIMessage` objects representing the conversation memory.

        Notes:
            - Sticky messages are always included in the memory, even if they exceed the memory limit.
            - If a "new topic" internal message is found, the system message is added to the memory.

        Example:
            memory_messages = conversation.get_memory_messages()
            for message in memory_messages:
                print(message.get_text())
        """
        temp_memory_list: list[AIMessage] = []
        new_topic_found: bool = False


        for message in reversed(self.__messages):
            if len(temp_memory_list) >= self.__max_memory_messages:
                if message.is_sticky():
                    temp_memory_list.append(message)
                continue

            if message.get_role() == AIC_ROLE_INTERNAL and message.get_text() == AIC_COMMAND_NEWTOPIC:
                new_topic_found = True
                break

            temp_memory_list.append(message)

        if new_topic_found:          #found a new topic (internal) message so we need to add system message
            temp_memory_list.append(self.__messages[0])

        temp_memory_list.reverse()

        return temp_memory_list

        

    def get_conversation_python_memory_payload(self, use_sticky:bool = False) -> list[dict[str, str]]:
        """ Returns the conversation as a payload to be sent to the AI model via the old API Style
        (i.e. not using https). This will only contains the last max_memory messages (plus the system prompt).
        """

        #traverse the list of messages from the last to first in order to check if there is an internal AIC_COMMAND_NEWTOPIC message
        #if found build a temporary memory list with only the messages after the AIC_COMMAND_NEWTOPIC message (+ the systememessages)
        #if not found proceed as usual
        temp_memory_list:list[AIMessage] = self.get_memory_messages()

        payload_msg_list:list[dict[str, str]] = []

        current_message:AIMessage = None

        for current_message in temp_memory_list:
            payload_msg_list.append(current_message.get_message_payload())

        return payload_msg_list

    def get_ith_message(self, i:int) -> AIMessage:
        """ Return the i-th message in the conversation. The system message is at index 0.
            Raise ValueError if the index is out of range.
        """
        length:int = len(self.__messages)
        if i < -length or i >= length:
            raise ValueError("Invalid message index: " + str(i))

        return self.__messages[i]

    def get_messages(self)-> list[AIMessage]:
        return self.__messages

    def get_conversation_python_history_payload(self) -> list[dict[str, str]]:
        """ Returns the conversation as a payload to be sent to the AI model via the old API Style
        (i.e. not using https). This will only contains the last max_memory messages (plus the system prompt)."""
        payload_msg_list:list[dict[str, str]] = []

        for message in self.__messages:
            payload_msg_list.append(message.get_message_payload())

        return payload_msg_list
    
    def toDict(self) -> dict[str, list[dict[str, str]]]:
        """ Returns the conversation as a dictionary to be sent to the AI model via the old API Style
        (i.e. not using https). This will only contains the last max_memory messages (plus the system prompt)."""
        payload_msg_list: list[dict[str, str]] = self.get_conversation_python_history_payload()

        return payload_msg_list


    def get_conversation_payload(self, l_temperature=0.7, l_top_p = 0.95, l_max_tokens = 4000) -> dict:
        """ Returns the conversation as a payload to be sent to the AI model. This will only contains the last max_memory messages (plus the system prompt)."""
        payload_msg_list = self.get_memory_messages()

        payload = { "messages": payload_msg_list, "temperature": l_temperature, "top_p": l_top_p, "max_tokens": l_max_tokens }
        return payload


    def get_conversation_history_payload(self, l_temperature=0.7, l_top_p = 0.95, l_max_tokens = 4000) -> dict:
        """ Returns the conversation as a payload to be sent to the AI model. """
        payload_msg_list = []
        for message in self.__messages:
            payload_msg_list.append(message.get_message_payload())

        payload = { "messages": payload_msg_list, "temperature": l_temperature, "top_p": l_top_p, "max_tokens": l_max_tokens }
        return payload

    def to_string(self, memory_only:bool = False, add_sticky:bool = True) -> str:
        counter:int = 0
        result:str = "\n"

        if memory_only:
            if add_sticky:
                result = result + "Memory Messages (including sticky)\n"
            else:
                result = result + "Memory Messages\n"
        else:
            result = result + "History Messages\n"
        
        result:str= f"\n{counter} -----------\n" 
        result += self.__messages[0].to_string() + "\n--"

        last_messages = self.__messages[1:] 

        for message in last_messages:
            counter += 1
            if memory_only:
                if add_sticky:
                    if message.is_sticky() or counter >= (len(self.__messages) - self.__max_memory_messages):
                        result = result + f"\n{counter}----------\n" + message.to_string() + "\n"
                else:
                    if counter >= (len(self.__messages) - self.__max_memory_messages):
                        result = result + f"\n{counter}----------\n" + message.to_string() + "\n"
            else:
                result = result + f"\n{counter}----------\n" + message.to_string() + "\n"

        return result
        

    def get_messages_copy(self) -> list[AIMessage]:
        """ Returns a copy of the list of messages in the conversation."""
        return self.__messages.copy()

    def count_non_sticky_messages(self) -> int:
        """ Count non sticky messages in the conversation.
        """
        count:int = 0
        for message in self.__messages:
            if not message.is_sticky():
                count += 1
        return count

    def count_sticky_messages(self) -> int:
        """ Count sticky messages in the conversation. 
        """
        count:int = 0
        for message in self.__messages:
            if message.is_sticky():
                count += 1
        return count

    def count_all_messages(self) -> int:
        """ Count all messages in the conversation. 
        """
        return len(self.__messages)

    def get_max_memory_messages(self) -> int:
        return self.__max_memory_messages

    def to_dict(self) -> dict[str, list[dict]]:
        return self.get_conversation_payload()
    
    def set_max_memory_messages(self, max_memory:int) -> None:
        if max_memory <= 0:     
            raise ValueError("Max memory must be > 0")
        self.__max_memory_messages = max_memory
        return

    def remove_messages(self, remove_n_messages:int = 1, remove_sticky:bool = True) -> None:
        """ Remove the last n messages from the conversation. 
            If remove_sticky is True, sticky messages will be removed as well.
            raise ValueError if you try to remove <0 messages. 
            SYSTEM_MESSAGE is never removed.
        """
        if remove_n_messages < 0:
            raise ValueError("You cannot remove a negative number of messages")

        msgs_to_remove: int = min(remove_n_messages, len(self.__messages)-1)
        if msgs_to_remove > 0:

            if remove_sticky:
                self.__messages = self.__messages[:-msgs_to_remove]
            else:
                msgs_to_remove: int = min(msgs_to_remove, self.count_non_sticky_messages())
                removed_count = 0
                for i in range(len(self.__messages) - 1, 0, -1):  # Start from the end
                    if not self.__messages[i].is_sticky():
                        del self.__messages[i]
                        removed_count += 1
                        if removed_count == msgs_to_remove:
                            break

                for _ in range(msgs_to_remove):
                    if not self.__messages[-1].is_sticky():
                        self.__messages = self.__messages[:-1]
                    else:
                        break
        else:
            return
        self.recalculate_tokens()
        return

    def remove_non_sticky_messages(self, remove_n_messages:int = 1) -> None:
        if remove_n_messages < 0:
            raise ValueError("You cannot remove a negative number of messages")
        
        self.remove_messages(remove_n_messages, False)
        return

    def restart(self) -> None:
        """ Remove all messages from the conversation except the system message.
        """
        self.__messages = [self.__messages[0]]
        return

    def recalculate_tokens(self) -> None:
        self.__user_tokens = 0
        self.__assistant_tokens = 0
        self.__total_tokens = 0
        self.__memory_user_tokens = 0
        self.__memory_assistant_tokens = 0
        self.__memory_total_tokens = 0
        self.__biggest_user_msg_tokens = 0
        self.__biggest_assistant_msg_tokens = 0
        i:int = 0   

        for message in self.__messages:
            i=i+1
            l_msg_tokens:int = message.get_estimated_tokens()
        
            if message.get_role() == AIC_ROLE_USER:
                self.__user_tokens += l_msg_tokens
                self.__total_tokens += l_msg_tokens
                if i > (len(self.__messages) - self.__max_memory_messages):
                    self.__memory_user_tokens += l_msg_tokens
                    self.__memory_total_tokens += l_msg_tokens
                if l_msg_tokens > self.__biggest_user_msg_tokens:
                    self.__biggest_user_msg_tokens = l_msg_tokens
        
            elif message.get_role() == AIC_ROLE_ASSISTANT:
                self.__assistant_tokens += l_msg_tokens
                self.__total_tokens += l_msg_tokens
                if i > (len(self.__messages) - self.__max_memory_messages):
                    self.__memory_assistant_tokens += l_msg_tokens
                    self.__memory_total_tokens += l_msg_tokens
                if l_msg_tokens > self.__biggest_assistant_msg_tokens:
                    self.__biggest_assistant_msg_tokens = l_msg_tokens
        
            elif message.get_role() in [AIC_ROLE_SYSTEM, AIC_ROLE_DEVELOPER]:
                self.__system_message_tokens = l_msg_tokens
                self.__total_tokens += l_msg_tokens
                self.__memory_total_tokens += l_msg_tokens
        return

    def get_system_prompt(self) -> str:
        return self.__messages[0].get_text()
    
    def get_messages_count(self, memory_only:bool=False, count_sticky:bool = False, count_internal:bool = False) -> int:
        """
        Return the number of messages in the conversation, including the system message.

        Args:
            memory_only (bool): If True, only count messages within the memory limit.
            add_sticky (bool): If True and memory_only is True, include sticky messages in the count.

        Returns:
            int: The number of messages in the conversation.

        The method calculates the number of messages in the conversation based on the specified conditions:
        - If memory_only is True, it counts up to the maximum memory messages plus one.
        - If add_sticky is True and memory_only is True, it also counts sticky messages that are not in the last `result` messages.
        - If memory_only is False, it counts all messages in the conversation.
        """
        result:int           = 0
        sticky_counted:int   = 0
        internal_counted:int = 0
        system_message_reached:bool = False

        for message in reversed(self.__messages):

            if (memory_only and (result >= self.__max_memory_messages)) or system_message_reached:
                break

            if message.is_internal():
                internal_counted += 1

            if message.is_sticky():
                sticky_counted += 1


            if message.is_internal() and not count_internal:
                continue
            if message.is_sticky() and not count_sticky:
                continue
            if message.get_role() in [AIC_ROLE_SYSTEM, AIC_ROLE_DEVELOPER]:
                system_message_reached = True

            result += 1

        if not system_message_reached:
            result += 1

        """
    
        if memory_only:
            result = min(len(self.__messages), self.__max_memory_messages+1)

            #now add all sticky messages not in the last result ones
            if add_sticky:
                #get the first "len of messages list - result messages" messages
                messages_to_check = self.__messages[:-result]

                for message in messages_to_check:
                    if message.is_sticky() and message.get_role() not in [AIC_ROLE_SYSTEM, AIC_ROLE_DEVELOPER, AIC_ROLE_INTERNAL]:
                        result += 1
        else:
            result = len(self.__messages)
        
        """
        return result
    
    def get_memory_messages_no(self) -> int:
        return min(len(self.__messages), self.__max_memory_messages+1)
    
    def get_last_message_text(self) -> str:
        return self.__messages[-1].get_text()
    
    def set_last_message_stickiness(self, sticky:bool) -> None:
        self.__messages[-1].set_sticky(sticky)
        return
    
    def set_nth_message_stickiness(self, nth:int, sticky:bool) -> None:

        if (nth >= 1) and len(self.__messages) > nth:
            self.__messages[nth].set_sticky(sticky)   
        return


    def set_last_TWO_messages_stickiness(self, sticky:bool) -> None:
        current_len:int = len(self.__messages)
        if current_len >= 1:
            self.__messages[-1].set_sticky(sticky)
        if current_len >= 2:
            self.__messages[-2].set_sticky(sticky)
        return  
    

    def print(self, memory_only:bool = False, add_sticky:bool = True, text_only:bool = False) -> int:
        """
        Print the whole list of messages and return the number of elements actually printed.

        Args:
            memory_only (bool): If True, only print messages that are within the memory limit.
            add_sticky (bool): If True and memory_only is True, include sticky messages in the print (even if not in the memory limit).
            text_only (bool): If True, only print the text content of the messages without additional metadata.

        Returns:
            int: The number of messages actually printed.

        The method iterates through the list of messages and prints them based on the specified conditions.
        It uses ANSI escape codes to color the output based on the role of the message (user, assistant, system).
        If the message type is an image URL, it prints the URL differently based on its format.
        """
    
        to_print:bool = False
        counter:int = 0
        printed_count:int = 0

        for message in self.__messages:
            
            if message.get_role() == AIC_ROLE_SYSTEM:
                to_print = True
            else:
                if memory_only:
                    if add_sticky:
                        if message.is_sticky() or counter >= (len(self.__messages) - self.__max_memory_messages):
                            to_print = True
                    else:
                        if counter >= (len(self.__messages) - self.__max_memory_messages):
                            to_print = True
                else:
                    to_print = True
                    
            if to_print:
                THE_CONTENT_COLOR:str = COLOR_WHITE

                if message.get_role() == AIC_ROLE_USER:
                    THE_CONTENT_COLOR = COLOR_WHITE
                elif message.get_role() == AIC_ROLE_ASSISTANT:
                    THE_CONTENT_COLOR = COLOR_LIGHT_GREEN
                elif message.get_role() == AIC_ROLE_SYSTEM:
                    THE_CONTENT_COLOR = COLOR_YELLOW
                if not text_only:
                    print(COLOR_CYAN.format(f"{counter} ------------------------------------------ {self.__messages[counter].get_role().upper()} (type={self.__messages[counter].get_type()}, sticky={self.__messages[counter].is_sticky()}):"))
                print(THE_CONTENT_COLOR.format(f"{self.__messages[counter].get_text()}\n"))
                #print(f"{counter}: {self.__messages[counter].get_role()}:")
                #print(f"{self.__messages[counter].get_text()}")
        
                if self.__messages[counter].get_type() == AIC_TYPE_IMAGE_URL:
                    image_url: str = self.__messages[counter].get_url()
                    if image_url.startswith("data:image"):
                        print(THE_CONTENT_COLOR .format(f"{image_url[:30]}...{image_url[-30:]}"))
                        #print(f"{image_url[:30]}...{image_url[-30:]}")
                    else:
                        print(THE_CONTENT_COLOR .format(f"{image_url}"))
                        #print(f"{image_url}")
                printed_count += 1

            counter += 1
            to_print = False
        return printed_count

    def print2(self, memory_only:bool = False, add_sticky:bool = True, add_internal:bool = False, text_only:bool = False) -> int:
        """
        Print the whole list of messages and return the number of elements actually printed.

        Args:
            memory_only (bool): If True, only print messages that are within the memory limit.
            add_sticky (bool): If True and memory_only is True, include sticky messages in the print (even if not in the memory limit).
            text_only (bool): If True, only print the text content of the messages without additional metadata.

        Returns:
            int: The number of messages actually printed.

        The method iterates through the list of messages and prints them based on the specified conditions.
        It uses ANSI escape codes to color the output based on the role of the message (user, assistant, system).
        If the message type is an image URL, it prints the URL differently based on its format.
        """
    
        """
        COLOR_RED:str    = "\033[91m {}\033[00m"
        COLOR_DARK_GREEN:str   = "\033[32m {}\033[00m"
        COLOR_BLUE:str   = "\033[94m {}\033[00m"
        COLOR_PINK:str   = "\033[95m {}\033[00m"
        COLOR_BLACK:str  = "\033[98m {}\033[00m"
        COLOR_GRAY:str   = "\033[99m {}\033[00m"
        """ 

        my_add_internal:bool = add_internal
        if memory_only:
            my_add_internal = False
            temp_memory_list:list[AIMessage] = self.get_memory_messages()
        else:
            temp_memory_list = self.__messages

        counter:int = 0
        printed_count:int = 0

        for message in temp_memory_list:
            
            current_role:str = message.get_role()
            if current_role == AIC_ROLE_INTERNAL and not my_add_internal:
                continue

            THE_CONTENT_COLOR:str = COLOR_WHITE

            if current_role == AIC_ROLE_USER:
                THE_CONTENT_COLOR = COLOR_WHITE
            elif current_role == AIC_ROLE_ASSISTANT:
                THE_CONTENT_COLOR = COLOR_LIGHT_GREEN
            elif current_role in [AIC_ROLE_SYSTEM, AIC_ROLE_DEVELOPER]:
                THE_CONTENT_COLOR = COLOR_YELLOW
            elif current_role == AIC_ROLE_INTERNAL:
                THE_CONTENT_COLOR = COLOR_GRAY
            else:
                THE_CONTENT_COLOR = COLOR_WHITE

            if not text_only:
                print(COLOR_CYAN.format(f"{counter}. {temp_memory_list[counter].get_role().upper()} (type={temp_memory_list[counter].get_type()}, sticky={temp_memory_list[counter].is_sticky()}):"))
            print(THE_CONTENT_COLOR.format(f"{temp_memory_list[counter].get_text()}\n"))
            #print(f"{counter}: {self.__messages[counter].get_role()}:")
            #print(f"{self.__messages[counter].get_text()}")
    
            if self.__messages[counter].get_type() == AIC_TYPE_IMAGE_URL:
                image_url: str = self.__messages[counter].get_url()
                if image_url.startswith("data:image"):
                    print(THE_CONTENT_COLOR .format(f"{image_url[:30]}...{image_url[-30:]}"))
                    #print(f"{image_url[:30]}...{image_url[-30:]}")
                else:
                    print(THE_CONTENT_COLOR .format(f"{image_url}"))
                    #print(f"{image_url}")
            printed_count += 1
            counter += 1
            
        return printed_count


    def print_specific_message(self, index: int, text_only: bool = False) -> bool:
        """
        Print a specific message by index. Return False if the index-th message does not exist

        Args:
            index (int): The index of the message to print.
            text_only (bool): If True, only print the text content of the message without additional metadata.
        """
        result = False
        if 0 <= index < len(self.__messages):
            message = self.__messages[index]
            THE_CONTENT_COLOR:str = "\033[97m"  # Default to white

            if message.get_role() == AIC_ROLE_USER:
                THE_CONTENT_COLOR = "\033[97m"  # White
            elif message.get_role() == AIC_ROLE_ASSISTANT:
                THE_CONTENT_COLOR = "\033[92m"  # Light green
            elif message.get_role() == AIC_ROLE_SYSTEM:
                THE_CONTENT_COLOR = "\033[93m"  # Yellow

            if not text_only:
                print(f"\033[96m{index} ------------------------------------------ {message.get_role().upper()} (type={message.get_type()}, sticky={message.is_sticky()}):\033[00m")
            print(f"{THE_CONTENT_COLOR}{message.get_text()}\033[00m\n")

            if message.get_type() == AIC_TYPE_IMAGE_URL:
                image_url: str = message.get_url()
                if image_url.startswith("data:image"):
                    print(f"{THE_CONTENT_COLOR}{image_url[:30]}...{image_url[-30:]}\033[00m")
                else:
                    print(f"{THE_CONTENT_COLOR}{image_url}\033[00m")
            result = True
        else:
            print(f"Invalid message index: {index}. Must be between 0 and {len(self.__messages) - 1}.")
        return result

if __name__ == '__main__':
    print("AIConversation.py - not an executable module.")