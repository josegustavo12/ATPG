`timescale 1ns/1ps  // Define a escala de tempo

module EXEMPLO_AND_TB;
  reg x, y;         // Entradas como registradores
  wire out;         // Saída como fio

  // Instanciando o módulo a ser testado
  EXEMPLO_AND uut (.x(x), .y(y), .out(out));

  initial begin
    $dumpfile("exemplo.vcd");
    $dumpvars(0, EXEMPLO_AND_TB);
    // Monitorando as variáveis para exibir os valores
    $monitor("Tempo: %0t | x = %b | y = %b | out = %b", $time, x, y, out);

    // Testando diferentes valores para x e y
    x = 0; y = 0; #10;  // Espera 10 unidades de tempo
    x = 0; y = 1; #10;
    x = 1; y = 0; #10;
    x = 1; y = 1; #10;

    // Finaliza a simulação
    $finish;
  end
endmodule
