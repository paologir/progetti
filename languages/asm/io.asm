section .data
    prompt db 'Inserisci un numero: ', 0
    len_prompt equ $ - prompt

section .bss
    num resb 5          ; buffer per il numero inserito

section .text
    global _start

_start:
    ; stampa il prompt
    mov eax, 4          ; syscall per write
    mov ebx, 1          ; file descriptor 1 (stdout)
    mov ecx, prompt     ; indirizzo del prompt
    mov edx, len_prompt ; lunghezza del prompt
    int 0x80            ; chiamata di sistema

    ; legge il numero
    mov eax, 3          ; syscall per read
    mov ebx, 0          ; file descriptor 0 (stdin)
    mov ecx, num        ; indirizzo del buffer
    mov edx, 5          ; lunghezza del buffer
    int 0x80            ; chiamata di sistema

    ; stampa il numero
    mov eax, 4          ; syscall per write
    mov ebx, 1          ; file descriptor 1 (stdout)
    mov ecx, num        ; indirizzo del numero
    mov edx, 5          ; lunghezza del numero
    int 0x80            ; chiamata di sistema

    ; exit(0)
    mov eax, 1          ; syscall per exit
    mov ebx, 0          ; status code 0
    int 0x80            ; chiamata di sistema
