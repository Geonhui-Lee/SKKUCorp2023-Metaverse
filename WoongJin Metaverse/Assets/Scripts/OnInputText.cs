using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using OpenAI;
using static System.Net.Mime.MediaTypeNames;
using System.Linq;
using System.Threading;
using Unity.VisualScripting;

public class OnInputText : MonoBehaviour
{
    public GameObject UserCanvas;
    public GameObject NPCCanvas;
    public GameObject NPC;
    public TMP_InputField inputField;
    public TextMeshProUGUI UserText;
    public TextMeshProUGUI NPCText;

    private OpenAIApi openai = new OpenAIApi();
    private CancellationTokenSource token = new CancellationTokenSource();
    private bool OnTrigger = false;

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
            SendMessage(inputField.text);
            inputField.text = "";
            yield return new WaitForSeconds(2f);
            UserCanvas.SetActive(false);
        }
        
    }

    private new void SendMessage(string UserText)
    {

        var message = new List<ChatMessage>
            {
                new ChatMessage()
                {
                    Role = "system",
                    Content = prompt
                },

                new ChatMessage()
                {
                    Role = "user",
                    Content = UserText
                }
            };

        openai.CreateChatCompletionAsync(new CreateChatCompletionRequest()
        {
            Model = "gpt-3.5-turbo-0301",
            Messages = message,
            Stream = true
        }, HandleResponse, null, token);
    }

    private void HandleResponse(List<CreateChatCompletionResponse> responses)
    {
        NPCText.text = string.Join("", responses.Select(r => r.Choices[0].Delta.Content));
    }

    private void OnDestroy()
    {
        token.Cancel();
    }

    IEnumerator Typing(string text)
    {
        foreach (char letter in text)
        {
           NPCText.text += letter;
           yield return new WaitForSeconds(0.2f);
        }

    }
}
