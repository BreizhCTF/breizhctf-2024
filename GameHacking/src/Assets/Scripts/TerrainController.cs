using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class TerrainController : MonoBehaviour
{

    public GameObject keyObj;

    void Start()
    {
        Vector3 size = GetComponent<Collider>().bounds.size;
        Vector3 pos = transform.position;
        for (int z = 0; z < 300; z++)
        {
            float real_z = pos.z + z * (size.z / 16F);
            for (int x = ((z < 16) ? 0 : 7); x < ((z < 16) ? 16 : 10); x++)
            {
                float real_x = pos.x + x * (size.x / 16F);
                for (int y = 0; y < ((z < 16) ? 16 : 3); y++)
                {
                    float real_y = pos.y + y * (60F / 16F);
                    GameObject new_keyObj = Instantiate(keyObj);
                    new_keyObj.SetActive(true);
                    ((Renderer)new_keyObj.GetComponent<Renderer>()).enabled = false;
                    new_keyObj.transform.position = new Vector3(real_x, real_y, real_z);
                }
            }
        }
    }

    void Update()
    {
        
    }
}
