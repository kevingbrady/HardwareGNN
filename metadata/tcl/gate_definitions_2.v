module AND2X1(Q,Y,X,OUT,IN1,IN2,A,B);
    input IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and2_1 inst(.A(IN1|A),.B(IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NAND2X1(Q,QN,Y,X,OUT,IN1,IN2,A,B);
    input IN1,IN2,A,B; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand2_1 inst(.A(IN1|A),.B(IN2|B),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NAND3X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand3_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module SDFFSRX1(CK,D,SI,SE,SET,RESET,Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,C,SN,RN);
    input CK,D,SI,SE,SET,RESET,IN1,IN2,IN3,A,B,C,SN,RN; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__sdfxtp_1 inst(.CLK(CK),.D(D|(IN1|A)),.SCD(SI),.SCE(SE),.Q(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module INVX1(Q,QN,Y,X,OUT,IN1,IN,A);
    input IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_1 inst(.A(IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module MX2X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,S0,S);
    input IN1,IN2,IN3,A,B,S0,S; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__mux2_1 inst(.A0(IN1|A),.A1(IN2|B),.S(IN3|S0|S),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NAND4X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,A,B,C,D);
    input IN1,IN2,IN3,IN4,A,B,C,D; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand4_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.D(IN4|D),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module MUX21X2(Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,S);
    input IN1,IN2,IN3,A,B,S; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__mux2_2 inst(.A0(IN1|A),.A1(IN2|B),.S(IN3|S),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AND2X2(Q,Y,X,OUT,IN1,IN2,A,B);
    input IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and2_2 inst(.A(IN1|A),.B(IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module INVX0(Q,QN,Y,X,OUT,ZN,IN1,IN,A,INP);
    input IN1,IN,A,INP; output Q,QN,Y,X,OUT,ZN;
    sky130_fd_sc_hd__inv_1 inst(.A(IN1|IN|A|INP),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q; assign ZN=Q;
endmodule


module AND4X1(Q,Y,X,OUT,IN1,IN2,IN3,IN4,A,B,C,D);
    input IN1,IN2,IN3,IN4,A,B,C,D; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and4_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.D(IN4|D),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NOR2X0(Q,QN,Y,X,OUT,IN1,IN2,A,B);
    input IN1,IN2,A,B; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor2_1 inst(.A(IN1|A),.B(IN2|B),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module DFFNX2(Q,QN,Y,X,OUT,CLK,CK,D,IN);
    input CLK,CK,D,IN; output Q,QN,Y,X,OUT; wire clk_inv;
    sky130_fd_sc_hd__inv_2 u_clkinv(.A(CLK|CK),.Y(clk_inv));
    sky130_fd_sc_hd__dfxtp_2 inst(.CLK(clk_inv),.D(D|IN),.Q(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OR4X1(Q,Y,X,OUT,IN1,IN2,IN3,IN4,A,B,C,D);
    input IN1,IN2,IN3,IN4,A,B,C,D; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or4_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.D(IN4|D),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OR2X1(Q,Y,X,OUT,IN1,IN2,A,B);
    input IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or2_1 inst(.A(IN1|A),.B(IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module XOR2X1(Q,Y,X,OUT,IN1,IN2,A,B);
    input IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__xor2_1 inst(.A(IN1|A),.B(IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OA21X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,A1,A2,A0,B1,B0);
    input IN1,IN2,IN3,A1,A2,A0,B1,B0; output Q,QN,Y,X,OUT; wire or2_out;
    sky130_fd_sc_hd__or2_1 u_or2(.A(IN1|A1|A0),.B(IN2|A2),.X(or2_out));
    sky130_fd_sc_hd__and2_1 u_and2(.A(or2_out),.B(IN3|B1|B0),.X(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OR3X1(Q,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or3_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module ISOLANDX1(Q,QN,Y,X,OUT,D,IN1,ISO,IN2);
    input D,IN1,ISO,IN2; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__and2_1 inst(.A(D|IN1),.B(ISO|IN2),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AO22X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,A0,A1,A2,B0,B1,B2);
    input IN1,IN2,IN3,IN4,A0,A1,A2,B0,B1,B2; output Q,QN,Y,X,OUT; wire and_a, and_b;
    sky130_fd_sc_hd__and2_1 u_and_a(.A(IN1|A0|A1),.B(IN2|A1|A2),.X(and_a));
    sky130_fd_sc_hd__and2_1 u_and_b(.A(IN3|B0|B1),.B(IN4|B1|B2),.X(and_b));
    sky130_fd_sc_hd__or2_1 u_or(.A(and_a),.B(and_b),.X(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AND3X1(Q,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and3_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module XNOR2X1(Q,Y,X,OUT,IN1,IN2,A,B);
    input IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__xnor2_1 inst(.A(IN1|A),.B(IN2|B),.Y(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NOR2X1 (Y, A, B);
    input A, B; output Y;
    sky130_fd_sc_hd__nor2_1 inst (.A(A), .B(B), .Y(Y));
endmodule

module NOR3X0(Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor3_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NOR4X0(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,A,B,C,D);
    input IN1,IN2,IN3,IN4,A,B,C,D; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor4_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.D(IN4|D),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NAND2X0(Q,QN,Y,X,OUT,IN1,IN2,A,B);
    input IN1,IN2,A,B; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand2_1 inst(.A(IN1|A),.B(IN2|B),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NAND3X0(Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand3_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule


module NAND4X0(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,A,B,C,D);
    input IN1,IN2,IN3,IN4,A,B,C,D; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand4_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.D(IN4|D),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AOI21X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,A1,A2,A0,B1,B0);
    input IN1,IN2,IN3,A1,A2,A0,B1,B0; output Q,QN,Y,X,OUT; wire and2_out;
    sky130_fd_sc_hd__and2_1 u_and2(.A(IN1|A1|A0),.B(IN2|A2),.X(and2_out));
    sky130_fd_sc_hd__nor2_1 u_nor2(.A(and2_out),.B(IN3|B1|B0),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AOI22X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,A0,A1,A2,B0,B1,B2);
    input IN1,IN2,IN3,IN4,A0,A1,A2,B0,B1,B2; output Q,QN,Y,X,OUT; wire and1_out, and2_out;
    sky130_fd_sc_hd__and2_1 u_and1(.A(IN1|A0|A1),.B(IN2|A1|A2),.X(and1_out));
    sky130_fd_sc_hd__and2_1 u_and2(.A(IN3|B0|B1),.B(IN4|B1|B2),.X(and2_out));
    sky130_fd_sc_hd__nor2_1 u_nor(.A(and1_out),.B(and2_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OA221X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1);
    input IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1; output Q,QN,Y,X,OUT; wire or_a, or_b;
    sky130_fd_sc_hd__or2_1 u_or_a(.A(IN1|A1),.B(IN2|A2),.X(or_a));
    sky130_fd_sc_hd__or2_1 u_or_b(.A(IN3|B1),.B(IN4|B2),.X(or_b));
    sky130_fd_sc_hd__and3_1 u_and(.A(or_a),.B(or_b),.C(IN5|C1),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module BUFX1(Q,QN,Y,X,OUT,IN1,A);
    input IN1,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__buf_1 inst(.A(IN1|A),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AO21X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,A1,A2,B1);
    input IN1,IN2,IN3,A1,A2,B1; output Q,QN,Y,X,OUT; wire and2_out;
    sky130_fd_sc_hd__and2_1 u_and2(.A(IN1|A1),.B(IN2|A2),.X(and2_out));
    sky130_fd_sc_hd__or2_1 u_or2(.A(and2_out),.B(IN3|B1),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OA22X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,A1,A2,B1,B2);
    input IN1,IN2,IN3,IN4,A1,A2,B1,B2; output Q,QN,Y,X,OUT; wire or_a, or_b;
    sky130_fd_sc_hd__or2_1 u_or_a(.A(IN1|A1),.B(IN2|A2),.X(or_a));
    sky130_fd_sc_hd__or2_1 u_or_b(.A(IN3|B1),.B(IN4|B2),.X(or_b));
    sky130_fd_sc_hd__and2_1 u_and(.A(or_a),.B(or_b),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NBUFFX2(Q,QN,Y,X,OUT,IN1,IN,A);
    input IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__buf_2 inst(.A(IN1|IN|A),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OA222X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2);
    input IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2; output Q,QN,Y,X,OUT; wire or_a, or_b, or_c;
    sky130_fd_sc_hd__or2_1 u_or_a(.A(IN1|A1),.B(IN2|A2),.X(or_a));
    sky130_fd_sc_hd__or2_1 u_or_b(.A(IN3|B1),.B(IN4|B2),.X(or_b));
    sky130_fd_sc_hd__or2_1 u_or_c(.A(IN5|C1),.B(IN6|C2),.X(or_c));
    sky130_fd_sc_hd__and3_1 u_and(.A(or_a),.B(or_b),.C(or_c),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AO222X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2);
    input IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2; output Q,QN,Y,X,OUT; wire and_a, and_b, and_c;
    sky130_fd_sc_hd__and2_1 u_and_a(.A(IN1|A1),.B(IN2|A2),.X(and_a));
    sky130_fd_sc_hd__and2_1 u_and_b(.A(IN3|B1),.B(IN4|B2),.X(and_b));
    sky130_fd_sc_hd__and2_1 u_and_c(.A(IN5|C1),.B(IN6|C2),.X(and_c));
    sky130_fd_sc_hd__or3_1 u_or(.A(and_a),.B(and_b),.C(and_c),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AO221X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1);
    input IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1; output Q,QN,Y,X,OUT; wire and_a, and_b;
    sky130_fd_sc_hd__and2_1 u_and_a(.A(IN1|A1),.B(IN2|A2),.X(and_a));
    sky130_fd_sc_hd__and2_1 u_and_b(.A(IN3|B1),.B(IN4|B2),.X(and_b));
    sky130_fd_sc_hd__or3_1 u_or(.A(and_a),.B(and_b),.C(IN5|C1),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module XOR3X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT; wire xor_stage1;
    sky130_fd_sc_hd__xor2_1 u_xor_a(.A(IN1|A),.B(IN2|B),.X(xor_stage1));
    sky130_fd_sc_hd__xor2_1 u_xor_b(.A(xor_stage1),.B(IN3|C),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module XNOR3X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT; wire xor_stage1;
    sky130_fd_sc_hd__xor2_1 u_xor(.A(IN1|A),.B(IN2|B),.X(xor_stage1));
    sky130_fd_sc_hd__xnor2_1 u_xnor(.A(xor_stage1),.B(IN3|C),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OAI21X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,A1,A2,A0,B1,B0);
    input IN1,IN2,IN3,A1,A2,A0,B1,B0; output Q,QN,Y,X,OUT; wire or_out;
    sky130_fd_sc_hd__or2_1 u_or(.A(IN1|A1|A0),.B(IN2|A2),.X(or_out));
    sky130_fd_sc_hd__nand2_1 u_nand(.A(or_out),.B(IN3|B1|B0),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OAI22X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,A1,A2,B1,B2);
    input IN1,IN2,IN3,IN4,A1,A2,B1,B2; output Q,QN,Y,X,OUT; wire or_a, or_b;
    sky130_fd_sc_hd__or2_1 u_or_a(.A(IN1|A1),.B(IN2|A2),.X(or_a));
    sky130_fd_sc_hd__or2_1 u_or_b(.A(IN3|B1),.B(IN4|B2),.X(or_b));
    sky130_fd_sc_hd__nand2_1 u_nand(.A(or_a),.B(or_b),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AOI222X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2);
    input IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2; output Q,QN,Y,X,OUT; wire and_a, and_b, and_c;
    sky130_fd_sc_hd__and2_1 u_and_a(.A(IN1|A1),.B(IN2|A2),.X(and_a));
    sky130_fd_sc_hd__and2_1 u_and_b(.A(IN3|B1),.B(IN4|B2),.X(and_b));
    sky130_fd_sc_hd__and2_1 u_and_c(.A(IN5|C1),.B(IN6|C2),.X(and_c));
    sky130_fd_sc_hd__nor3_1 u_nor(.A(and_a),.B(and_b),.C(and_c),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AOI221X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1);
    input IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1; output Q,QN,Y,X,OUT; wire and_a, and_b;
    sky130_fd_sc_hd__and2_1 u_and_a(.A(IN1|A1),.B(IN2|A2),.X(and_a));
    sky130_fd_sc_hd__and2_1 u_and_b(.A(IN3|B1),.B(IN4|B2),.X(and_b));
    sky130_fd_sc_hd__nor3_1 u_nor(.A(and_a),.B(and_b),.C(IN5|C1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module SDFFX1(Q,QN,Y,X,OUT,D,IN1,SI,SE,CLK,CK);
    input D,IN1,SI,SE,CLK,CK; output Q,QN,Y,X,OUT; wire q_out;
    sky130_fd_sc_hd__sdfxtp_1 inst(.CLK(CLK|CK),.D(D|IN1),.SCD(SI),.SCE(SE),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module LSDNENX1(Q,QN,Y,X,OUT,D,IN1,ENB,GATE_N);
    input D,IN1,ENB,GATE_N; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__dlxtn_1 inst(.D(D|IN1),.GATE_N(ENB|GATE_N),.Q(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module MUX21X1(Q,QN,Y,X,OUT,IN1,IN2,A0,A1,S);
    input IN1,IN2,A0,A1,S; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__mux2_1 inst(.A0(IN1|A0),.A1(IN2|A1),.S(S),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module DFFX2(Q,QN,Y,X,OUT,CLK,CK,D,IN1);
    input CLK,CK,D,IN1; output Q,QN,Y,X,OUT; wire q_out;
    sky130_fd_sc_hd__dfxtp_2 inst(.CLK(CLK|CK),.D(D|IN1),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module LARX1(Q,QN,Y,X,OUT,D,IN1,CLK,GATE,RSTB,RESET_B);
    input D,IN1,CLK,GATE,RSTB,RESET_B; output Q,QN,Y,X,OUT; wire q_out;
    sky130_fd_sc_hd__dlrtp_1 inst(.D(D|IN1),.GATE(CLK|GATE),.RESET_B(RSTB|RESET_B),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module HADDX1(SO,SUM,C1,COUT,A0,A,B0,B);
    input A0,A,B0,B; output SO,SUM,C1,COUT; wire s_out, c_out;
    sky130_fd_sc_hd__ha_1 inst(.A(A0|A),.B(B0|B),.COUT(c_out),.SUM(s_out));
    assign SO=s_out; assign SUM=s_out; assign C1=c_out; assign COUT=c_out;
endmodule

module INVX8(Q,QN,Y,X,OUT,IN1,IN,A);
    input IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_8 inst(.A(IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NAND3X4(Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand3_4 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OAI222X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2);
    input IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2; output Q,QN,Y,X,OUT; wire or_a, or_b, or_c;
    sky130_fd_sc_hd__or2_1 u_or_a(.A(IN1|A1),.B(IN2|A2),.X(or_a));
    sky130_fd_sc_hd__or2_1 u_or_b(.A(IN3|B1),.B(IN4|B2),.X(or_b));
    sky130_fd_sc_hd__or2_1 u_or_c(.A(IN5|C1),.B(IN6|C2),.X(or_c));
    sky130_fd_sc_hd__nand3_1 u_nand(.A(or_a),.B(or_b),.C(or_c),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module OAI221X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1);
    input IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1; output Q,QN,Y,X,OUT; wire or_a, or_b;
    sky130_fd_sc_hd__or2_1 u_or_a(.A(IN1|A1),.B(IN2|A2),.X(or_a));
    sky130_fd_sc_hd__or2_1 u_or_b(.A(IN3|B1),.B(IN4|B2),.X(or_b));
    sky130_fd_sc_hd__nand3_1 u_nand(.A(or_a),.B(or_b),.C(IN5|C1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NOR2X2(Q,QN,Y,X,OUT,IN1,IN2,A,B);
    input IN1,IN2,A,B; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor2_2 inst(.A(IN1|A),.B(IN2|B),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NOR4X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,IN4,A,B,C,D);
    input IN1,IN2,IN3,IN4,A,B,C,D; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor4_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.D(IN4|D),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module LSDNX1(Q,QN,Y,X,OUT,D,IN1);
    input D,IN1; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__buf_1 inst(.A(D|IN1),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module NOR3X1(Q,QN,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor3_1 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module AND3X4(Q,Y,X,OUT,IN1,IN2,IN3,A,B,C);
    input IN1,IN2,IN3,A,B,C; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and3_4 inst(.A(IN1|A),.B(IN2|B),.C(IN3|C),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module DFFARX1(Q,QN,Y,X,OUT,CLK,CK,D,IN1,RSTB,RESET_B);
    input CLK,CK,D,IN1,RSTB,RESET_B; output Q,QN,Y,X,OUT; wire q_out;
    sky130_fd_sc_hd__dfrtp_1 inst(.CLK(CLK|CK),.D(D|IN1),.RESET_B(RSTB|RESET_B),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module SDFFARX1(Q,QN,Y,X,OUT,CLK,CK,D,IN1,SI,SCD,SE,SCE,RSTB,RESET_B);
    input CLK,CK,D,IN1,SI,SCD,SE,SCE,RSTB,RESET_B; output Q,QN,Y,X,OUT; wire q_out;
    sky130_fd_sc_hd__sdfrtp_1 inst(.CLK(CLK|CK),.D(D|IN1),.RESET_B(RSTB|RESET_B),.SCD(SI|SCD),.SCE(SE|SCE),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module FADDX1(S,SUM,CO,COUT,A,B,CI,CIN);
    input A,B,CI,CIN; output S,SUM,CO,COUT; wire s_out, c_out;
    sky130_fd_sc_hd__fa_1 inst(.A(A),.B(B),.CIN(CI|CIN),.COUT(c_out),.SUM(s_out));
    assign S=s_out; assign SUM=s_out; assign CO=c_out; assign COUT=c_out;
endmodule

module DFFX1(Q,QN,Y,X,OUT,CLK,CK,D,IN1);
    input CLK,CK,D,IN1; output Q,QN,Y,X,OUT; wire q_out;
    sky130_fd_sc_hd__dfxtp_1 inst(.CLK(CLK|CK),.D(D|IN1),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule



