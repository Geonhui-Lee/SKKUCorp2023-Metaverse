using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Move : MonoBehaviour
{
    public float speed = 5f;
    [SerializeField]
    public Animator anmi;

    void Update()
    {
        if (Input.GetKey(KeyCode.LeftArrow))
        {
            transform.Translate(-speed * Time.deltaTime, 0, 0);
            anmi.SetBool("isRunning", true);
        }
        else if (Input.GetKey(KeyCode.RightArrow))
        {
            transform.Translate(speed * Time.deltaTime, 0, 0);
            anmi.SetBool("isRunning", true);
        }
        else if (Input.GetKey(KeyCode.UpArrow))
        {
            transform.Translate(0, 0, speed * Time.deltaTime);
            anmi.SetBool("isRunning", true);
        }
        else if (Input.GetKey(KeyCode.DownArrow))
        {
            transform.Translate(0, 0, -speed * Time.deltaTime);
            anmi.SetBool("isRunning", true);
        }
        anmi.SetBool("isRunning", false);
    }
}