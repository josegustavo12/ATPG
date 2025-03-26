`timescale 1ns/1ps
module tb;

  reg N1;
  reg N2;
  reg N3;
  reg N6;
  reg N7;
  wire N22;
  wire N23;

  c17 uut (.N1(N1), .N2(N2), .N3(N3), .N6(N6), .N7(N7), .N22(N22), .N23(N23));
  initial begin
    // Aplicando vetor 1
    N1 = 0;
    N2 = 0;
    N3 = 0;
    N6 = 1;
    N7 = 0;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("1. OUTPUT: N22 = %b", N22);
    $display("1. OUTPUT: N23 = %b", N23);

    // Aplicando vetor 2
    N1 = 0;
    N2 = 1;
    N3 = 0;
    N6 = 0;
    N7 = 0;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("2. OUTPUT: N22 = %b", N22);
    $display("2. OUTPUT: N23 = %b", N23);

    // Aplicando vetor 3
    N1 = 1;
    N2 = 0;
    N3 = 0;
    N6 = 1;
    N7 = 1;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("3. OUTPUT: N22 = %b", N22);
    $display("3. OUTPUT: N23 = %b", N23);

    // Aplicando vetor 4
    N1 = 1;
    N2 = 0;
    N3 = 0;
    N6 = 0;
    N7 = 1;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("4. OUTPUT: N22 = %b", N22);
    $display("4. OUTPUT: N23 = %b", N23);

    // Aplicando vetor 5
    N1 = 1;
    N2 = 0;
    N3 = 1;
    N6 = 1;
    N7 = 1;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("5. OUTPUT: N22 = %b", N22);
    $display("5. OUTPUT: N23 = %b", N23);

    // Aplicando vetor 6
    N1 = 0;
    N2 = 1;
    N3 = 1;
    N6 = 0;
    N7 = 0;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("6. OUTPUT: N22 = %b", N22);
    $display("6. OUTPUT: N23 = %b", N23);

    // Aplicando vetor 7
    N1 = 1;
    N2 = 0;
    N3 = 1;
    N6 = 0;
    N7 = 1;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("7. OUTPUT: N22 = %b", N22);
    $display("7. OUTPUT: N23 = %b", N23);

    // Aplicando vetor 8
    N1 = 0;
    N2 = 0;
    N3 = 1;
    N6 = 0;
    N7 = 1;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("8. OUTPUT: N22 = %b", N22);
    $display("8. OUTPUT: N23 = %b", N23);

    // Aplicando vetor 9
    N1 = 1;
    N2 = 1;
    N3 = 1;
    N6 = 0;
    N7 = 1;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("9. OUTPUT: N22 = %b", N22);
    $display("9. OUTPUT: N23 = %b", N23);

    // Aplicando vetor 10
    N1 = 1;
    N2 = 1;
    N3 = 1;
    N6 = 0;
    N7 = 1;

    #5;
    // Falha solicitada sem porta definida; selecionado aleatoriamente 'N10'
    force uut.N10 = 1;  // Injetando falha: stuck-at 1 em N10
    #10;
    $display("10. OUTPUT: N22 = %b", N22);
    $display("10. OUTPUT: N23 = %b", N23);

    $finish;
  end
endmodule