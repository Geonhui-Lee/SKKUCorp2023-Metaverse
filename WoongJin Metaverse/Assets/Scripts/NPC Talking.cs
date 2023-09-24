using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class NPCTalking : MonoBehaviour
{
    public TextMeshProUGUI dialogText;


    void Start()
    {
        string[] textList;
        string sampleText = "HHIHIHIHIHIHIHHIHIHI\nLOLOLOLOLOLOLOLOL";
        textList = sampleText.Split('\n');
        StartCoroutine(Typing(textList));
    }

    void Update()
    {

    }

    IEnumerator Typing(string[] textList)
    {
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
