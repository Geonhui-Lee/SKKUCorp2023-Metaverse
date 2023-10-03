using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using MySql.Data.MySqlClient;
using System;


public class DetectObject : MonoBehaviour
{
    [SerializeField] public float detectionRadius = 5f;
    private HashSet<GameObject> detectedObjects = new HashSet<GameObject>();
    public TextMeshProUGUI npcText;

    string connectionString = "Server=127.0.0.1;Database=status;User=root;Password=crossfire03;";


    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRadius);
    }

    void Update()
    {
        Collider[] colliders = Physics.OverlapSphere(transform.position, detectionRadius);

        List<GameObject> objectsToRemove = new List<GameObject>();

        foreach (GameObject obj in detectedObjects)
        {
            float distance = Vector3.Distance(obj.transform.position, transform.position);
            if (distance > detectionRadius)
            {
                objectsToRemove.Add(obj);
            }
        }

        foreach (GameObject obj in objectsToRemove)
        {
            detectedObjects.Remove(obj);
        }

        foreach (Collider collider in colliders)
        {
            if (collider.CompareTag("NPC"))
            {
                if (!detectedObjects.Contains(collider.gameObject))
                {
                    ObjectState objectState = collider.GetComponent<ObjectState>();
                    if (objectState != null)
                    {
                        SaveToDatabase("NPC 상태: " + objectState.state);
                    }

                    detectedObjects.Add(collider.gameObject);
                }
            }
            if (collider.CompareTag("PizzaNPC"))
            {
                if(!detectedObjects.Contains(collider.gameObject))
                {
                    ObjectState objectState = collider.GetComponent<ObjectState>();
                    if (objectState != null)
                    {
                        SaveToDatabase("PizzaNPC 상태: " + objectState.state);
                    }

                    detectedObjects.Add(collider.gameObject);
                }
            }
            if (collider.CompareTag("Oven"))
            {
                if(!detectedObjects.Contains(collider.gameObject))
                {
                    ObjectState objectState = collider.GetComponent<ObjectState>();
                    if (objectState != null)
                    {
                        SaveToDatabase("Oven 상태: " + objectState.state);
                    }

                    detectedObjects.Add(collider.gameObject);
                }
            }
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.tag == "NPCTalking")
        {
            Debug.Log("NPC와 상호작용함");
            string dialogueText = npcText.text;
            Debug.Log("NPC의 대화 내용: " + dialogueText);
        }
    }

    private void SaveToDatabase(string npcState)
{
    try
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            connection.Open();
            using (MySqlCommand cmd = new MySqlCommand())
            {
                cmd.Connection = connection;
                cmd.CommandText = "INSERT INTO npc_states (state) VALUES (@state)";
                cmd.Parameters.AddWithValue("@state", npcState);
                cmd.ExecuteNonQuery();
            }
        }
    }
    catch (Exception ex)
    {
        Debug.LogError("Error saving to database: " + ex.Message);
    }
}
}
