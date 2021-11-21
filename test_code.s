section .data
cadena: db "Hello world", 10, 0
numero: db 265

section .text
global inicio
inicio:
push rbp
mov rbp,rsp
mov rax,1
mov rdi,1
mov rsi,cadena
mov rdx,12
syscall
mov rax,30
add rax,30
mov rsp,rbp
pop rbp
mov rdi,0
syscall