using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ExplosionController : MonoBehaviour
{
    private long ttl;


    void Start()
    {
        ttl = 30;
    }


    void FixedUpdate()
    {
        ttl--;
        if (ttl <= 0) Destroy(this.gameObject);
    }
}
