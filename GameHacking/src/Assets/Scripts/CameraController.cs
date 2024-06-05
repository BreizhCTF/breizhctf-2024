using Cinemachine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraController : MonoBehaviour
{
    private CinemachineVirtualCamera main_cam, back_cam;

    void Start()
    {
        foreach(CinemachineVirtualCamera cam in FindObjectsOfType<CinemachineVirtualCamera>())
        {
            switch(cam.name)
            {
                case "FollowCamera":
                    main_cam = cam;
                    break;
                case "BackFollowCamera":
                    back_cam = cam;
                    break;
            }
        }
        main_cam.enabled = true;
        back_cam.enabled = false;
    }


    void Update()
    {
        if (Input.GetMouseButtonDown(1))
        {
            main_cam.enabled = !main_cam.enabled;
            back_cam.enabled = !main_cam.enabled;
        }
    }
}
