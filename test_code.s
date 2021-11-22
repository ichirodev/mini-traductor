section .data
cadena: db "Hello world", 10, 0
numero: db 255

section .text
global inicio
inicio:
push rbp
mov rbp,rsp
mov rax,1
mov rdi,1
mov rsi,cadena
mov rbx,numero
mov rdx,12
mov rax,4
mov rbx,1
mov rcx,cadena
mov rdx,12
syscall
mov rax,30
add rax,30
add rax,numero
mov rbx,20
add rax,rbx
mov rbx,3
mov rcx,12
mul rcx
sub rax,900
div rax,rbx
mov rsp,rbp
pop rbp
mov rax,1
mov rdi,0
syscall