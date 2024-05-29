#include <Python.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/aes.h>

#include "mmm.h"

char hint[] = "MMM stands for Module Maze Madness :-)";

uint8_t key[] = {0x67, 0x74, 0x6a, 0x94, 0x95, 0x34, 0xac, 0x3d, 0x80, 0x19, 0x82};

uint8_t maze[15][15] = {
        {0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
        {1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1},
        {1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1},
        {1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1},
        {1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1},
        {1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1},
        {1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1},
        {1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1},
        {1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1},
        {1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1},
        {1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1},
        {1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1},
        {1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1},
        {1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2},
        {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1}
};

coord_t player = {0, 0};

EVP_MD_CTX *mdctx;

void decrypt_aes_cbc(const unsigned char *encrypted_data, size_t encrypted_data_len,
                     const unsigned char *key, const unsigned char *iv, unsigned char * out) {
    AES_KEY aes_key;
    if (AES_set_decrypt_key(key, 128, &aes_key) < 0) {
        return;
    }

    AES_cbc_encrypt(encrypted_data, out, encrypted_data_len, &aes_key, iv, AES_DECRYPT);
}

static PyObject * get_flag(PyObject * self, PyObject *args) {
    unsigned char * user_key;
    if(!PyArg_ParseTuple(args, "y", &user_key)) {
        return NULL;
    }

    unsigned char ciphertext[] = {
            0x1d, 0xad, 0x71, 0x23, 0xd3, 0x3e, 0x5e, 0x82, 0x8c, 0xb5, 0xe4, 0xd8,
            0x52, 0x9a, 0x30, 0x80, 0x10, 0x66, 0x9f, 0xcb, 0xe9, 0x4d, 0x7e, 0x97,
            0x48, 0x89, 0xab, 0x7f, 0xe2, 0xad, 0x6f, 0x28, 0xa7, 0x71, 0x1e, 0x72,
            0x99, 0x14, 0x5d, 0x87, 0x3c, 0x4a, 0x66, 0xc6, 0xd7, 0x4c, 0x0d, 0x2d,
            0x62, 0x30, 0xdb, 0xe4, 0xd3, 0xc5, 0x82, 0x3c, 0x34, 0x52, 0xde, 0x1a,
            0xbd, 0x32, 0xfd, 0xa0, 0x95, 0xf0, 0xf6, 0x63, 0xd0, 0xaa, 0x6b, 0x27,
            0xb9, 0x2a, 0x38, 0xba, 0xb5, 0x3b, 0x4b, 0xed, 0x22, 0x7d, 0x92, 0x97,
            0xf5, 0x66, 0xf0, 0xcc, 0x46, 0x81, 0x91, 0x56, 0xf3, 0xaf, 0xda, 0x4a,
            0x29, 0x37, 0x9e, 0x21, 0x2f, 0x9d, 0xe6, 0xa5, 0xdb, 0xe4, 0xc5, 0x2d,
            0x45, 0xa1, 0xd9, 0x06, 0xc2, 0xdc, 0x1a, 0xbc, 0xed, 0x12, 0x58, 0xff,
            0xb6, 0x5a, 0x63, 0xfa, 0x6a, 0x1f, 0x3c, 0x74
    };
    unsigned int ciphertext_len = 128;
    unsigned char iv[] = "0123456789012345";

    char * plaintext = malloc(ciphertext_len);

    decrypt_aes_cbc(ciphertext, ciphertext_len, user_key, iv, plaintext);
    return Py_BuildValue("s", plaintext);
}


static PyMethodDef MadnessMethods[] = {
        {"get_flag", get_flag, METH_VARARGS, "Get the flag"},
        {NULL, NULL, 0, NULL} // Sentinel
};

// Module definition
static struct PyModuleDef Madness = {
        PyModuleDef_HEAD_INIT,
        "madness", // Module name
        NULL,            // Module documentation
        -1,              // Size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
        MadnessMethods   // Method table
};

// Module initialization function
PyMODINIT_FUNC PyInit_Madness(void) {
    return PyModule_Create(&Madness);
}


bool check_in_bounds(coord_t coord) {
    return coord.x >= 0 && coord.x < 14 && coord.y >= 0 && coord.y < 15;
}

static PyObject * move_right(PyObject * self, PyObject *args) {
    if(!check_in_bounds((coord_t) {player.x, player.y + 1})) {
        return Py_BuildValue("s", "Cannot move right.");
    }
    if(maze[player.x][player.y + 1] == 1) {
        return Py_BuildValue("s", "Cannot move right.");
    }
    player.y++;
    char data[3];
    snprintf(data, 3, "%x%x", player.x, player.y);
    EVP_DigestUpdate(mdctx, data, 2);
    return Py_BuildValue("s", "Moved right.");
}

static PyObject * move_left(PyObject * self, PyObject *args) {
    if(!check_in_bounds((coord_t) {player.x, player.y - 1})) {
        return Py_BuildValue("s", "Cannot move left.");
    }
    if(maze[player.x][player.y - 1] == 1) {
        return Py_BuildValue("s", "Cannot move left.");
    }
    player.y--;
    char data[3];
    snprintf(data, 3, "%x%x", player.x, player.y);
    EVP_DigestUpdate(mdctx, data, 2);
    return Py_BuildValue("s", "Moved left.");
}

static PyObject * move_up(PyObject * self, PyObject *args) {
    if(!check_in_bounds((coord_t) {player.x - 1, player.y})) {
        return Py_BuildValue("s", "Cannot move up.");
    }
    if(maze[player.x - 1][player.y] == 1) {
        return Py_BuildValue("s", "Cannot move up.");
    }
    player.x--;
    char data[3];
    snprintf(data, 3, "%x%x", player.x, player.y);
    EVP_DigestUpdate(mdctx, data, 2);
    return Py_BuildValue("s", "Moved up.");
}

static PyObject * move_down(PyObject * self, PyObject *args) {
    if(!check_in_bounds((coord_t) {player.x + 1, player.y})) {
        return Py_BuildValue("s", "Cannot move down.");
    }
    if(maze[player.x + 1][player.y] == 1) {
        return Py_BuildValue("s", "Cannot move down.");
    }
    player.x++;
    char data[3];
    snprintf(data, 3, "%x%x", player.x, player.y);
    EVP_DigestUpdate(mdctx, data, 2);
    return Py_BuildValue("s", "Moved down.");
}

static PyObject * check_solved(PyObject * self, PyObject *args) {
    if(maze[player.x][player.y] == 2) {
        unsigned char *md5_digest;
        unsigned int md5_digest_len = EVP_MD_size(EVP_md5());

        md5_digest = (unsigned char *)OPENSSL_malloc(md5_digest_len);
        EVP_DigestFinal_ex(mdctx, md5_digest, &md5_digest_len);
        EVP_MD_CTX_free(mdctx);

        char output[33];

        for(int i = 0; i < 16; i++) {
            sprintf(&output[i*2], "%02x", (unsigned int)md5_digest[i]);
        }

        char *data = malloc(200);
        snprintf(data, 200, "Solved. Here is your reward: %s", output);
        return Py_BuildValue("s", data);
    }
    return Py_BuildValue("s", "Not solved.");
}

static PyMethodDef MazeMethods[] = {
        {"move_right", move_right, METH_NOARGS, "Move right"},
        {"move_left", move_left, METH_NOARGS, "Move left"},
        {"move_up", move_up, METH_NOARGS, "Move up"},
        {"move_down", move_down, METH_NOARGS, "Move down"},
        {"check_solved", check_solved, METH_NOARGS, "Check if solved"},
        {NULL, NULL, 0, NULL} // Sentinel
};

// Module definition
static struct PyModuleDef Maze = {
        PyModuleDef_HEAD_INIT,
        "maze", // Module name
        NULL,            // Module documentation
        -1,              // Size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
        MazeMethods   // Method table
};


// Module initialization function
PyMODINIT_FUNC PyInit_Maze(void) {
    mdctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(mdctx, EVP_md5(), NULL);
    return PyModule_Create(&Maze);
}


static PyObject * module_check(PyObject * self, PyObject *args) {
    srand(0x1337);
    const char *data;
    if(!PyArg_ParseTuple(args, "s", &data)) {
        return NULL;
    }

    size_t len = strlen(data);
    for(size_t i = 0; i < len; i++) {
        int r = rand() % 256;
        if((data[i] ^ r) != key[i]) {
            return Py_BuildValue("s", "Incorrect.");
        }
    }

    return Py_BuildValue("s", "Correct.");
}

static PyObject * module_welcome(PyObject * self, PyObject *args) {
    const char *data;
    if(!PyArg_ParseTuple(args, "s", &data)) {
        return NULL;
    }

    return Py_BuildValue("s", "Welcome in the matrix");
}


static PyMethodDef ModuleMethods[] = {
        {"welcome", module_welcome, METH_VARARGS, "Welcome"},
        {"check", module_check, METH_VARARGS, "Check something..."},
        {NULL, NULL, 0, NULL} // Sentinel
};

// Module definition
static struct PyModuleDef Module = {
        PyModuleDef_HEAD_INIT,
        "Module", // Module name
        NULL,            // Module documentation
        -1,              // Size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
        ModuleMethods   // Method table
};


// Module initialization function
PyMODINIT_FUNC PyInit_Module(void) {
    return PyModule_Create(&Module);
}
