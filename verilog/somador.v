module adder4 (
    input  [3:0] a,    // Primeiro operando de 4 bits
    input  [3:0] b,    // Segundo operando de 4 bits
    input        c,    // Carry in (1 bit)
    output [4:0] y     // Saída (5 bits): soma completa de a, b e c
);
    assign {y[4], y[3:0]} = a + b + c;

endmodule
