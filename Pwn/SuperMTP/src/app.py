#!/usr/bin/env python3
import lib.smtp as smtp

def menu():
    print("Menu:")
    print("1.\tAdd an email")
    print("2.\tShow pending mails")
    print("3.\tEdit an email")
    print("4.\tSend an email")
    return int(input(">>> "))



if __name__ == '__main__':
    print("---- SuperMTP ----")
    print(smtp.version())
    print("------------------")
    while True:
        match menu():
            case 1:
                fro = input("From: ")
                to   = input("To: ")
                subject = input("Subject: ")
                content = input("Content: ")
                print(smtp.gen_mail(fro, to, subject, content))
            case 2:
                mails = smtp.show_mails()
                for mail in mails.keys():
                    print(f"\t{mail}\t{mails[mail]}")
            case 3:
                index = int(input("Index: "))
                content = input("New content: ")
                smtp.edit_mail(index, content)
            case 4:
                index = int(input("Index: "))
                print(smtp.send_mail(index))
