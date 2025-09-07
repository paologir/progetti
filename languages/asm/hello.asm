section .data
    msg db 'Hello, World!', 0xA  ; stringa da stampare, 0xA è il carattere newline
    len equ $ - msg             ; lunghezza della stringa

section .text
    global _start

_start:
    ; write(1, msg, len)
    mov eax, 4          ; syscall per write
    mov ebx, 1          ; file descriptor 1 (stdout)
    mov ecx, msg        ; indirizzo della stringa
    mov edx, len        ; lunghezza della stringa
    int 0x80            ; chiamata di sistema

    ; exit(0)
    mov eax, 1          ; syscall per exit
    mov ebx, 0          ; status code 0
    int 0x80            ; chiamata di sistema
