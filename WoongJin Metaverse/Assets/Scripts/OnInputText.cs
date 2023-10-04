using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.IO;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using OpenAI;
using System.Threading;
using UnityEngine.Networking;
using System;

[System.Serializable]
public class MessageData {
    public string role;
    public string content;
}

[System.Serializable]
public class MessagesData
{
    public List<MessageData> messages;
}



public class OnInputText : MonoBehaviour
{
    public GameObject UserCanvas;
    public GameObject NPCCanvas;
    public GameObject NPC;
    public TMP_InputField inputField;
    public TextMeshProUGUI UserText;
    public TextMeshProUGUI NPCText;

    private bool OnTrigger = false;
    private string baseURL = "http://127.0.0.1:8000/";

    string prompt = "You *always* act like a villager. Talk as friendly as a friend, and talk as briefly as possible.";

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Return) && OnTrigger)
        {
            inputField.ActivateInputField();
            StartCoroutine(UserTalk());
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Player")
        {
            NPCCanvas.SetActive(true);
            OnTrigger = true;
        }
    }


    private void OnTriggerStay(Collider other)
    {
        if (other.tag == "Player")
        {
            NPC.transform.LookAt(other.transform);
            inputField.gameObject.SetActive(true);
            
        }

    }

    private void OnTriggerExit(Collider other)
    {
        if (other.tag == "Player")
        {
            NPCCanvas.SetActive(false);
            inputField.gameObject.SetActive(false);
            OnTrigger = false;
        }
    }


    IEnumerator UserTalk()
    {
        if (inputField.text != null)
        {
            UserCanvas.SetActive(true);
            UserText.text = inputField.text;
            StartCoroutine(SendMessage(UserText.text));
            inputField.text = "";
            yield return new WaitForSeconds(2f);
            UserCanvas.SetActive(false);
        }
        
    }

    private new IEnumerator SendMessage(string UserText)
    {
        ServicePointManager.ServerCertificateValidationCallback += (objSender, certificate, chain, sslPolicyError) => true;

        MessageData systemMessage = new MessageData();
        systemMessage.role = "system";
        systemMessage.content = prompt;

        MessageData userMessage = new MessageData();
        userMessage.role = "user";
        userMessage.content = UserText;

        MessagesData inputMessages = new MessagesData();
        List<MessageData> inputMessageList = new List<MessageData>
        {
            systemMessage,
            userMessage
        };
        inputMessages.messages = inputMessageList;

        string str = JsonUtility.ToJson(inputMessages);
        Debug.Log(str);

        //HttpWebRequest request = (HttpWebRequest)WebRequest.Create(baseURL);
        //Debug.Log(request);
        //request.Method = "POST";
        //request.ContentType = "application/json";
        //request.ContentLength = bytes.Length;
        //using (var stream = request.GetRequestStream())
        //{
        //    Debug.Log(stream);
        //    stream.Write(bytes, 0, bytes.Length);
        //    stream.Flush();
        //    stream.Close();
        //}
        using (UnityWebRequest request = UnityWebRequest.PostWwwForm(baseURL, str))
        {
            byte[] jsonToSend = new System.Text.UTF8Encoding().GetBytes(str);
            request.uploadHandler = new UploadHandlerRaw(jsonToSend);
            request.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.isNetworkError || request.isHttpError)
            {
                Debug.Log(request.error);
            }
            else
            {
                Debug.Log(request.downloadHandler.text);
            }

        }

        //HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        //Debug.Log(response);
        //StreamReader reader = new StreamReader(response.GetResponseStream());
        //string json = reader.ReadToEnd();
        //Debug.Log(json);
        //MessagesData info = JsonUtility.FromJson<MessagesData>(json);
        //Debug.Log(info);
        //NPCText.text = info.messages[info.messages.Count - 1].content;



        //WWWForm form = new WWWForm();


        //UnityWebRequest unityWebRequest = UnityWebRequest.Get(baseURL);
        //Debug.Log("Complete Request");

        //yield return unityWebRequest.SendWebRequest();

        //if(unityWebRequest.error == null)
        //{
        //    Debug.Log(unityWebRequest.downloadHandler.text);
        //    //Debug.Log(response);
        //    //StreamReader reader = new StreamReader(response.GetResponseStream());
        //    //string json = reader.ReadToEnd();
        //    //Debug.Log(json);
        //    //MessagesData info = JsonUtility.FromJson<MessagesData>(json);
        //    //Debug.Log(info);
        //    //NPCText.text = info.messages[info.messages.Count - 1].content;
        //    Debug.Log("Complete Response");
        //}

        //else
        //{
        //    Debug.Log("error");
        //    Debug.Log(unityWebRequest.error);
        //}


    }

    //private new void SendMessage(string UserText)
    //{

    //    var message = new List<ChatMessage>
    //        {
    //            new ChatMessage()
    //            {
    //                Role = "system",
    //                Content = prompt
    //            },

    //            new ChatMessage()
    //            {
    //                Role = "user",
    //                Content = UserText
    //            }
    //        };

    //    openai.CreateChatCompletionAsync(new CreateChatCompletionRequest()
    //    {
    //        Model = "gpt-3.5-turbo-0301",
    //        Messages = message,
    //        Stream = true
    //    }, HandleResponse, null, token);
    //}

    //private void HandleResponse(List<CreateChatCompletionResponse> responses)
    //{
    //    NPCText.text = string.Join("", responses.Select(r => r.Choices[0].Delta.Content));
    //}

    //private void OnDestroy()
    //{
    //    token.Cancel();
    //}

    IEnumerator Typing(string text)
    {
        foreach (char letter in text)
        {
           NPCText.text += letter;
           yield return new WaitForSeconds(0.2f);
        }

    }
}
