using Cinemachine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UIElements;

public class PlayerController : MonoBehaviour
{

    private Rigidbody body;
    public float speed;
    public float rot_speed;
    public GameObject keyObj;
    public Canvas health_lvl_obj;
    public Canvas flag1_obj, flag2_obj, flag3_obj, flag4_obj;
    private TextMeshProUGUI health_lvl_text;
    private TextMeshProUGUI flag1_text, flag2_text, flag3_text, flag4_text;
    private byte[] enc_flag_1 = { 246, 180, 78, 122, 246, 170, 78, 97, 65, 121, 165, 150, 66, 121, 166, 145, 85, 74, 181 };
    private byte[] enc_flag_2 = { 60, 86, 183, 99, 53, 91, 182, 116, 222, 74, 46, 114, 242, 90, 57, 121, 222, 93, 52, 116, 242, 118, 62, 111, 232, 77, 59, 120, 222, 75, 57, 123, 238, 91, 57, 66, 248, 70, 41, 66, 229, 64, 56 };
    private byte[] enc_flag_3 = { 2, 110, 89, 141, 6, 80, 74, 160, 97, 191, 10, 89, 98, 177, 44, 106, 121, 169, 22, 116, 73, 182, 22, 103, 98, 183, 29, 97, 73, 188, 26, 106, 122, 173 };
    private byte[] enc_flag_4 = { 99, 4, 55, 100, 72, 12, 40, 94, 132, 112, 208, 14, 185, 101, 220, 58, 141, 120, 221, 2, 185, 112, 193, 17, 142, 100, 193 };
    private byte[] flag1_hash = new byte[] { 0x85, 0x92, 0x16, 0x56, 0xc2, 0xdc, 0xc6, 0x24, 0x0c, 0x1b, 0xfc, 0x6a, 0x52, 0x75, 0xad, 0xb6, 0xe6, 0x44, 0x09, 0x42, 0x83, 0x41, 0x8a, 0x83, 0x4e, 0x14, 0x66, 0xdc, 0x76, 0x5f, 0x90, 0xd8, 0x49, 0x4e, 0x8d, 0x45, 0x59, 0x28, 0x21, 0x0a, 0x24, 0x13, 0x88, 0x29, 0xfa, 0xf9, 0xaa, 0x05, 0x33, 0xdd, 0xaf, 0x10, 0x03, 0x96, 0x11, 0x7b, 0xc0, 0xd3, 0x45, 0x5a, 0xca, 0xb9, 0x45, 0xa7 };
    private byte[] flag2_hash = new byte[] { 0x65, 0xaa, 0xed, 0xc8, 0x05, 0x48, 0x4c, 0x3e, 0x2b, 0xc9, 0x06, 0x89, 0xb0, 0x56, 0x7e, 0x39, 0xb3, 0xea, 0x94, 0xf7, 0x7e, 0x13, 0xf0, 0x4e, 0x35, 0x1e, 0x3a, 0x13, 0x35, 0xb9, 0x4a, 0xb2, 0x34, 0xa3, 0x21, 0xf2, 0x02, 0xbc, 0xef, 0x5b, 0x2b, 0x3d, 0xb6, 0xc6, 0x96, 0xd8, 0xce, 0xba, 0x92, 0xf0, 0x7c, 0x1d, 0x62, 0x45, 0x51, 0x02, 0x01, 0x20, 0x6a, 0xa1, 0x68, 0x6f, 0x18, 0xab };
    private byte[] flag3_hash = new byte[] { 0x38, 0xe9, 0x1c, 0xc3, 0x7c, 0xd4, 0x92, 0xe7, 0xa4, 0x84, 0xd1, 0xbc, 0xb5, 0xbc, 0x71, 0xcf, 0x3c, 0x2f, 0x44, 0xd7, 0x94, 0x73, 0xdf, 0x5d, 0xd4, 0xc4, 0x16, 0x9e, 0x36, 0xeb, 0x25, 0xe8, 0xb7, 0xc6, 0xff, 0xa8, 0x3e, 0xc9, 0x95, 0x88, 0xee, 0x54, 0x5c, 0xd5, 0xd3, 0x9b, 0x83, 0x4b, 0xaf, 0x2f, 0x39, 0x88, 0xab, 0x06, 0x39, 0x17, 0xa0, 0x33, 0xf6, 0x82, 0xa4, 0x5d, 0x7c, 0x82 };
    private byte[] flag4_hash = new byte[] { 0x46, 0x2b, 0x26, 0x53, 0x40, 0xa1, 0x32, 0x54, 0xd7, 0x05, 0x23, 0x02, 0x81, 0xa2, 0xa7, 0x07, 0x31, 0x42, 0x75, 0xea, 0xac, 0xfe, 0xfd, 0x12, 0xf8, 0x7d, 0x32, 0xef, 0x1f, 0xa7, 0x87, 0x30, 0xa5, 0xf1, 0x90, 0xf2, 0x00, 0x9f, 0xf4, 0xfb, 0x01, 0x43, 0x6b, 0xed, 0x69, 0xd8, 0x81, 0x16, 0x66, 0x47, 0xc9, 0xf5, 0xcf, 0x63, 0x0e, 0x81, 0x9f, 0x42, 0x3a, 0x7a, 0x04, 0x67, 0x0f, 0x4c };
    private Animator animator;
    private bool some_bool = false;
    private byte health = 255;
    private int sword_timer = 0;
    private bool on_ground = true;
    private bool flag1_triggered = false, flag2_triggered = false, flag3_triggered = false, flag4_triggered = false;
    private UnityEngine.Object ground_object = null;
    private CinemachineVirtualCamera main_cam, back_cam;
    public GameObject fireball_obj;
    private GameObject fireball = null;
    private int fireball_frames = 90;

    void Start()
    {
        health_lvl_text = ((RectTransform)health_lvl_obj.transform.GetChild(0)).GetComponent<TextMeshProUGUI>();
        flag1_text = ((RectTransform)flag1_obj.transform.GetChild(0)).GetComponent<TextMeshProUGUI>();
        flag2_text = ((RectTransform)flag2_obj.transform.GetChild(0)).GetComponent<TextMeshProUGUI>();
        flag3_text = ((RectTransform)flag3_obj.transform.GetChild(0)).GetComponent<TextMeshProUGUI>();
        flag4_text = ((RectTransform)flag4_obj.transform.GetChild(0)).GetComponent<TextMeshProUGUI>();
        OnTorchLit(new Vector3(0, 0, 0));
        body = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
        foreach (CinemachineVirtualCamera cam in FindObjectsOfType<CinemachineVirtualCamera>())
        {
            switch (cam.name)
            {
                case "FollowCamera":
                    main_cam = cam;
                    break;
                case "BackFollowCamera":
                    back_cam = cam;
                    break;
            }
        }
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space) && on_ground && fireball_frames >= 90)
        {
            animator.SetTrigger("jump");
            body.AddForce(0, 350, 0);
        }
        if (Input.GetMouseButtonDown(0) && fireball == null && on_ground && some_bool)
        {
            animator.SetTrigger("throw_fireball");
            fireball = Instantiate(fireball_obj);
            fireball.transform.localScale = new Vector3(0.5f, 0.5f, 0.5f);
            fireball_frames = 0;
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        foreach (ContactPoint contact in collision.contacts) {
            if (contact.point.y <= transform.position.y + 0.3)
            {
                on_ground = true;
                ground_object = collision.gameObject;
                animator.SetBool("on_ground", on_ground);
            }
        }
        if (!flag4_triggered)
        {
            Vector3 pos = collision.transform.position;
            UInt64[] flag_key = compute_flag_key(pos);
            string flag = decrypt_flag(enc_flag_4, flag_key, flag4_hash);
            if (flag.Length > 0)
            {
                flag4_triggered = true;
                flag4_text.text = flag;
                flag4_text.color = Color.green;
                Vector3 collider_pos = collision.collider.transform.position;
                flag4_text.transform.position = new Vector3(collider_pos.x-1.3f, collider_pos.y+2.5f, collider_pos.z);
                ((Renderer)collision.collider.GetComponent<Renderer>()).enabled = true;
            }
        }
    }

    void OnCollisionExit(Collision collision)
    {
        if (collision.gameObject == ground_object || ground_object == null) {
            on_ground = false;
            ground_object = null;
            animator.SetBool("on_ground", on_ground);
        }
    }

    private string decrypt_flag(byte[] enc_flag, UInt64[] key, byte[] flag_hash)
    {
        string flag = "";
        for (int i = 0; i < enc_flag.Length; i++)
        {
            if (i < 8) flag += (char)(enc_flag[i] ^ ((key[0] >> ((i % 4) * 8)) & 0xFF));
            else flag += (char)(enc_flag[i] ^ ((key[1] >> ((i % 4) * 8)) & 0xFF));
        }
        /*if(enc_flag.SequenceEqual(enc_flag_4))
        {
            string out_flag = "";
            for(int i = 0; i < flag.Length; i++)
            {
                out_flag += (UInt32) flag[i] + " ";
            }
            print(out_flag);
        }*/
        if (System.Text.Encoding.UTF8.GetByteCount(flag) == flag.Length)
        {
            flag = "BZHCTF{" + flag + "}";
            byte[] hash;
            using (SHA512 shaM = new SHA512Managed())
            {
                hash = shaM.ComputeHash(Encoding.UTF8.GetBytes(flag));
            }
            if (hash.SequenceEqual(flag_hash)) return flag;
        }
        return "";
    }

    public UInt64[] compute_flag_key(Vector3 pos)
    {
        double[] flag_key_double = new double[] { 15D, 15D, 15D };
        double factor = 15D;
        foreach (GameObject list_keyObj in GameObject.FindGameObjectsWithTag(keyObj.tag))
        {
            Vector3 list_keyObj_pos = list_keyObj.transform.position;
            float distanceSqr = Mathf.Sqrt(Mathf.Pow(list_keyObj_pos.x - Mathf.Floor(pos.x), 2) + Mathf.Pow(list_keyObj_pos.y - Mathf.Floor(pos.y), 2) + Mathf.Pow(list_keyObj_pos.z - Mathf.Floor(pos.z), 2));
            if (distanceSqr < 5)
            {
                flag_key_double[0] += factor * list_keyObj_pos.x;
                flag_key_double[1] += factor * (list_keyObj_pos.y + 15);
                flag_key_double[2] += factor * list_keyObj_pos.z;
                factor++;
            }
        }
        UInt64[] flag_key = new UInt64[] { (UInt64)(flag_key_double[0] * 100000D + flag_key_double[1]), (UInt64)(flag_key_double[2] * 100000D + flag_key_double[1]) };
        return flag_key;
    }

    public void OnTorchLit(Vector3 pos)
    {
        if (!flag3_triggered) {
            UInt64[] flag_key = compute_flag_key(pos);
            string flag = decrypt_flag(enc_flag_3, flag_key, flag3_hash);
            if (flag.Length > 0)
            {
                flag3_triggered = true;
                flag3_text.text = flag;
                flag3_text.color = Color.green;
            }
            else
            {
                flag3_text.text = "                          Light me up !";
                flag3_text.color = Color.yellow;
            }
        }
    }

    void FixedUpdate()
    {
        Vector3 pos = transform.position;
        if (pos.y < -20)
        {
            health = 255;
            transform.position = new Vector3(4, 5, 3);
            sword_timer = 0;
        }
        if (pos.z >= 97.28f && pos.z <= 229.32f && pos.x >= -0.25f && pos.x <= 7f && pos.y >= -4f && pos.y <= 1f)
        {
            animator.SetBool("on_sword", true);
            if (sword_timer <= 0)
            {
                int sub_health = (int)((pos.z - 97.28f) * 8f);
                if (health - sub_health <= 0)
                {
                    health = 255;
                    transform.position = new Vector3(4, 5, 3);
                    sword_timer = 0;
                }
                else
                {
                    health -= (byte)sub_health;
                    sword_timer = 100;
                }
                health_lvl_text.text = "Health: " + health;
            }
            else sword_timer--;
        }
        else animator.SetBool("on_sword", false);

        UInt64[] flag_key = compute_flag_key(pos);
        if (!flag1_triggered) {
            string flag = decrypt_flag(enc_flag_1, flag_key, flag1_hash);
            if (flag.Length > 0)
            {
                flag1_triggered = true;
                flag1_text.text = flag;
                flag1_text.color = Color.green;
            }
            else
            {
                flag1_text.text = "               Come closer...";
                flag1_text.color = Color.yellow;
            }
        }
        if (!flag2_triggered)
        {
            string flag = decrypt_flag(enc_flag_2, flag_key, flag2_hash);
            if (flag.Length > 0)
            {
                flag2_triggered = true;
                flag2_text.text = flag;
                flag2_text.color = Color.green;
            }
            else
            {
                flag2_text.text = "                           Cross the whole bridge...";
                flag2_text.color = Color.yellow;
            }
        }
        if (fireball_frames < 90) fireball_frames++;
        if (fireball != null)
        {
            fireball.transform.position = new Vector3(pos.x + transform.forward.x * 0.7f, pos.y + 1.5f + transform.forward.y, pos.z + transform.forward.z * 0.7f);
            if (fireball_frames >= 15 && !fireball.activeSelf) fireball.SetActive(true);
            Vector3 scale = fireball.transform.localScale;
            fireball.transform.localScale = new Vector3(scale.x + 0.2f, scale.y + 0.2f, scale.z + 0.2f);
            if (fireball_frames >= 45 && fireball != null) {
                Rigidbody fireball_body = fireball.GetComponent<Rigidbody>();
                fireball_body.AddForce(transform.forward * 1500);
                fireball = null;
            }
        }
        float vt_force = Input.GetAxis("Vertical");
        float hz_force = Input.GetAxis("Horizontal");
        if ((vt_force < 0 && main_cam.enabled) || (vt_force > 0 && !main_cam.enabled))
        {
            vt_force /= 1.5f;
            hz_force /= 1.5f;
        }
        Vector3 velocity = (Camera.main.transform.forward * vt_force /*+ Camera.main.transform.right * hz_force*/) * speed;
        velocity.y = body.velocity.y;
        if(velocity.y > 0 && transform.position.y <= 0) velocity.y = 0;
        if (fireball == null) transform.Translate(velocity * Time.deltaTime, Space.World);
        transform.Rotate(Vector3.up, hz_force * Time.deltaTime * rot_speed);
        animator.SetFloat("speed", vt_force);
    }
}