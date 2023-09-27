using System.Collections;
using System.Collections.Generic;
using OpenAI;
using TMPro;
using UnityEngine;

public class NPCTalking : MonoBehaviour
{
    public TextMeshProUGUI dialogText;
    public string sampleText;

    public IEnumerator Typing(string sampleText)
    {
        string[] textList;
        textList = sampleText.Split('\n');
        foreach (string text in textList)
        {
            dialogText.text = "";
            foreach (char letter in text.ToCharArray())
            {
                dialogText.text += letter;
                yield return new WaitForSeconds(0.2f);
            }
        }

    }

    
}
