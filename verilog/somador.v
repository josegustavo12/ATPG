module FullAdder (
    input A,      // Bit de entrada A
    input B,      // Bit de entrada B
    input Cin,    // Carry-in
    output Sum,   // Soma
    output Cout   // Carry-out
);
    assign Sum = A ^ B ^ Cin;           // Soma = XOR das entradas
    assign Cout = (A & B) | (Cin & (A ^ B)); // Carry = (A AND B) OR (Cin AND (A XOR B))
endmodule


module Adder4Bit (
    input [3:0] A,   // Entrada de 4 bits A
    input [3:0] B,   // Entrada de 4 bits B
    input Cin,       // Carry-in inicial
    output [3:0] Sum, // Resultado da soma de 4 bits
    output Cout       // Carry-out final
);
    wire C1, C2, C3; // Fios intermediários para carry-out

    // Instanciando 4 somadores completos (Full Adders)
    FullAdder FA0 (A[0], B[0], Cin,  Sum[0], C1);
    FullAdder FA1 (A[1], B[1], C1,   Sum[1], C2);
    FullAdder FA2 (A[2], B[2], C2,   Sum[2], C3);
    FullAdder FA3 (A[3], B[3], C3,   Sum[3], Cout);
    
endmodule
