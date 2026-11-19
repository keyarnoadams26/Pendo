#include <string>
#include <algorithm>
#include <cctype>
extern "C" {
// Small native helper: normalizes a user search phrase.
// This is a starter native module; Python app does not yet load it.
void pendo_normalize(const char* input, char* output, int capacity) {
    if (!input || !output || capacity <= 0) return;
    std::string s(input);
    std::transform(s.begin(), s.end(), s.begin(),
        [](unsigned char c){ return static_cast<char>(std::tolower(c)); });
    int n=std::min(static_cast<int>(s.size()), capacity-1);
    for (int i=0;i<n;i++) output[i]=s[i];
    output[n]='\0';
}
}
