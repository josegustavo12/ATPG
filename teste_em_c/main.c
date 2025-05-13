#include <stdio.h>
#include <stdlib.h>

int main() {
    int ret = system("atalanta c17.v");
    if (ret == -1) {
        perror("Erro ao executar o comando");
    }
    return 0;
}
