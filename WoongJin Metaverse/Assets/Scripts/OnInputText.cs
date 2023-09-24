using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class OnInputText : MonoBehaviour
{
    public GameObject canvas;
    public TMP_InputField inputField;
    public TextMeshProUGUI UserText;


    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Return))
        {
            StartCoroutine(UserTalk());
            inputField.IsActive();
        }
    }

    IEnumerator UserTalk()
    {
        if (inputField.text != null)
        {
            canvas.SetActive(true);
            UserText.text = inputField.text;
            inputField.text = "";
            yield return new WaitForSeconds(2f);
            canvas.SetActive(false);
        }
        
    }
}
