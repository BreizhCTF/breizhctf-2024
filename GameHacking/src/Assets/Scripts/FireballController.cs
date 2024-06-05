using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FireballController : MonoBehaviour
{
    private long ttl;
    public GameObject explosion_obj;
    public PlayerController playerController;

    void Start()
    {
        ttl = 100;
    }

    void explode()
    {
        GameObject explosion = Instantiate(explosion_obj);
        explosion.transform.position = transform.position;
        explosion.SetActive(true);
        Destroy(this.gameObject);
    }

    void OnCollisionEnter(Collision collision)
    {
        GameObject target = collision.gameObject;
        if(target.name == "Torch")
        {
            playerController.OnTorchLit(collision.transform.position);
        }
        if (ttl <= 100-31) explode();
    }

    void FixedUpdate()
    {
        ttl--;
        if (ttl <= 0) explode();
    }
}
