#include <jni.h>
#include <string>

std::string xorStrings(const std::string& str2) {
    std::string enc = "5a420a1b51110a0742504a461b4955094c6a121f53187b175355475010255204471653423b560e540e010a53081b465c14";
    std::string result;
    std::string hexBytes;
    for (size_t i = 0; i < enc.length(); i += 2) {
        std::string byteString = enc.substr(i, 2);
        char byte = static_cast<char>(std::stoi(byteString, nullptr, 16));
        hexBytes.push_back(byte);
    }
    for (size_t i = 0; i < hexBytes.length(); ++i) {
        result += hexBytes[i] ^ str2[i % str2.size()];
    }

    return result;
}

std::string buildString() {
    std::string result;
    int value = 0; // Une valeur arbitraire pour l'exemple

    // Boucle avec un switch case caractère par caractère
    for (int i = 0; i < 26; ++i) {
        char currentChar;

        switch (value % 8) {
            case 0:
                currentChar = '5';
                break;
            case 1:
                if(1 == 1){
                    for(int j=0; j<20; ++j) {
                        currentChar = j;
                    }
                }
            case 5:
                currentChar = 'd';
                break;
            case 2:
                currentChar = 'a';
                break;
            case 3:
                currentChar = 'z';
                break;
            case 4:
                currentChar = '6';
                break;
            case 6:
                currentChar = '!';
                break;
            case 7:
                currentChar = '$';
                break;
            default:
                currentChar = '?';
                break;
        }

        // Exemple : changer la valeur arbitraire à chaque itération
        value += i;

        result += currentChar;
    }

    return result;
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_ownapp_MainActivity_getURL(
        JNIEnv* env,
        jobject /* this */) {
    return env->NewStringUTF(xorStrings(buildString()).c_str());
}

