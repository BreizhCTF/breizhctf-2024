#include <Python.h>
#include <stdbool.h>
#include <stdint.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>
#include <openssl/evp.h>

#define MESSAGE_SIZE 4096

struct message {
  size_t sz_message;
  char message[MESSAGE_SIZE];
} typedef message_t;

struct email {
  void (*send)(struct email *);
  char from[1024];
  char to[1024];
  char subject[1024];
  message_t  * msg;
} typedef email_t;


email_t * EMAILS[40];

int find_unused_email() {
  for(int i = 0; i < 40; i++) {
    if(!EMAILS[i]) {
      return i;
    }
  }
  return -1;
}

static PyObject* smtp_version(PyObject* self, PyObject* args) {
    char version[40];
    sprintf(version, "SuperMTP - Version %p", &EMAILS);

    return Py_BuildValue("s", version);
}

static bool parse_email(const char * email) {
  const char *atSymbol = strchr(email, '@');
  if(!atSymbol) {
    return false;
  }

  const char *dotSymbol = strchr(atSymbol, '.');
  if(!dotSymbol) {
    return false;
  }

  return true;
}

void send_wip(email_t *this) {
  char command[MESSAGE_SIZE];
  snprintf(command, MESSAGE_SIZE, "./sendmail.sh \"%s\" \"%s\" \"%s\"", this->from, this->to, this->msg->message);
  system(command);
  free(this->msg);
  free(this);
}

void send(email_t *this) {
  free(this->msg);
  free(this);
}

char *base64_decode(const char *input, int length) {
    BIO *b64, *bio;
    BUF_MEM *bptr = NULL;
    size_t length_out;
    char *buffer = NULL;

    b64 = BIO_new(BIO_f_base64());
    BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);
    bio = BIO_new_mem_buf((void *)input, length);
    bio = BIO_push(b64, bio);

    buffer = (char *)malloc(length);
    if (!buffer) {
        fprintf(stderr, "Failed to allocate memory.\n");
        exit(EXIT_FAILURE);
    }

    length_out = BIO_read(bio, buffer, length);
    BIO_free_all(bio);

    return buffer;
}


static PyObject* smtp_send_mail(PyObject* self, PyObject* args) {
  int index;
  if(!PyArg_ParseTuple(args, "i", &index)) {
    return Py_BuildValue("s", "Invalid argument.");
  } else if (index < 0 || index >= 40) {
    return Py_BuildValue("s", "Invalid argument.");
  }

   if(EMAILS[index]) {
     email_t * mail = EMAILS[index];
     mail->send(mail); // should be free at this moment.
     EMAILS[index] = 0;
   } else {
    return Py_BuildValue("s", "No email at that index.");
   }

   return Py_BuildValue("s", "Mail sent!");
}

static PyObject* smtp_gen_mail(PyObject* self, PyObject* args) {
  const char *from;
  const char *to;
  const char *subject;
  const char *message;
  const char *decoded_message;
  if(!PyArg_ParseTuple(args, "ssss", &from, &to, &subject, &message)) {
    return Py_BuildValue("s", "Invalid arguments.");
  }

  if(!parse_email(from) || !parse_email(to)) {
    return Py_BuildValue("s", "Invalid emails !");
  }

  decoded_message = base64_decode(message, strlen(message));

  char formatted_message[4096];
  message_t * msg = malloc(sizeof(message_t));

  msg->sz_message = snprintf(formatted_message, MESSAGE_SIZE, "DATA\n%s", decoded_message);
  strncpy(msg->message, formatted_message, MESSAGE_SIZE);

  email_t * new_mail = malloc(sizeof(email_t));
  new_mail->send = send;
  strncpy(new_mail->from, from, 1024);
  strncpy(new_mail->to, to, 1024);
  strncpy(new_mail->subject, subject, 1024);
  new_mail->msg  =  msg;

  int idx = find_unused_email();
  if(idx == -1) {
    free(new_mail->msg);
    free(new_mail);
    return Py_BuildValue("s", "No space left on device.");
  } else {
    EMAILS[idx] = new_mail;
  }
  return Py_BuildValue("s", "Email successfuly registered!");
}

static PyObject* smtp_show_pending(PyObject * self, PyObject *args) {
  PyObject* dict = PyDict_New();
  if(!dict) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to create dictionary");
        return NULL;
  }

  for(int i = 0; i < 40; ++i) {
    if(EMAILS[i]) {
      email_t * email = EMAILS[i];
      char key[20];
      char data[200];
      snprintf(data, 200, "Subject: %s", email->subject);
      snprintf(key, 20, "%d", i);
      PyDict_SetItemString(dict, key, PyUnicode_FromString(data));
    }
  }

  return dict;
}

static PyObject* smtp_edit_mail(PyObject * self, PyObject *args) {
  int index;
  const char * new_message;
  const char * decoded;
  if(!PyArg_ParseTuple(args, "is", &index, &new_message)) {
    return Py_BuildValue("s", "Invalid arguments.");
  }

  decoded = base64_decode(new_message, strlen(new_message));

  if(index > 0 && index < 40) {
    if(EMAILS[index]) {
      email_t *email_to_edit = EMAILS[index];
      if((strlen(new_message) + 5) < email_to_edit->msg->sz_message) {
        snprintf(email_to_edit->msg->message, email_to_edit->msg->sz_message, "DATA\n%s", decoded);
      } else {
        return Py_BuildValue("s", "Not implemented. :(");
      }
    } else {
      return Py_BuildValue("s", "Email does not exist.");
    }
  } else {
    return Py_BuildValue("s", "Invalid index.");
  }
  return Py_BuildValue("s", "Message edited!");
}


// Method table
static PyMethodDef smtp_methods[] = {
    {"version", smtp_version, METH_NOARGS, "Return a greeting message"},
    {"gen_mail", smtp_gen_mail, METH_VARARGS, "Generate an email."},
    {"show_mails", smtp_show_pending, METH_NOARGS, "Show pending mails."},
    {"send_mail", smtp_send_mail, METH_VARARGS, "Send a mail."},
    {"edit_mail", smtp_edit_mail, METH_VARARGS, "Edit a mail."},
    {NULL, NULL, 0, NULL}   // Sentinel
};

// Module definition
static struct PyModuleDef smtp_module = {
    PyModuleDef_HEAD_INIT,
    "smpt",          // Module name
    "Super MTP",   // Module documentation
    -1,                 // Size of per-interpreter state, -1 means global
    smtp_methods     // Method table
};

// Module initialization function
PyMODINIT_FUNC PyInit_smtp(void) {
    return PyModule_Create(&smtp_module);
}

