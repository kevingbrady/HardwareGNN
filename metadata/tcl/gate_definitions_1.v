module nor2s1(Q,QN,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd2s1(Q,QN,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module hi1s1(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__buf_1 inst(.A(DIN|IN1|IN|A),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module i1s1(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_1 inst(.A(DIN|IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module xor2s1(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__xor2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and2s1(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and3s1(Q,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and4s1(Q,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and4_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nor3s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nor4s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor4_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module or2s1(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module or3s1(Q,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module or4s1(Q,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or4_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd3s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd4s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand4_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nor5s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E; output Q,QN,Y,X,OUT; wire tmp;
    sky130_fd_sc_hd__nor4_1 u_nor4(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.Y(tmp));
    sky130_fd_sc_hd__nor2_1 u_nor2(.A(tmp),.B(DIN5|IN5|E),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module or5s1(Q,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E; output Q,Y,X,OUT; wire tmp;
    sky130_fd_sc_hd__or4_1 u_or4(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.X(tmp));
    sky130_fd_sc_hd__or2_1 u_or2(.A(tmp),.B(DIN5|IN5|E),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and5s1(Q,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E; output Q,Y,X,OUT; wire tmp;
    sky130_fd_sc_hd__and4_1 u_and4(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.X(tmp));
    sky130_fd_sc_hd__and2_1 u_and2(.A(tmp),.B(DIN5|IN5|E),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and9s1(Q,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,DIN7,DIN8,DIN9,IN1,IN2,IN3,IN4,IN5,IN6,IN7,IN8,IN9,A,B,C,D,E,F,G,H,I);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,DIN7,DIN8,DIN9,IN1,IN2,IN3,IN4,IN5,IN6,IN7,IN8,IN9,A,B,C,D,E,F,G,H,I; output Q,Y,X,OUT; wire tmp1, tmp2;
    sky130_fd_sc_hd__and4_1 u_and4_a(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.X(tmp1));
    sky130_fd_sc_hd__and4_1 u_and4_b(.A(DIN5|IN5|E),.B(DIN6|IN6|F),.C(DIN7|IN7|G),.D(DIN8|IN8|H),.X(tmp2));
    sky130_fd_sc_hd__and3_1 u_and3(.A(tmp1),.B(tmp2),.C(DIN9|IN9|I),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nb1s1(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_1 inst(.A(DIN|IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd4s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand4_4 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nor6s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A,B,C,D,E,F);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A,B,C,D,E,F; output Q,QN,Y,X,OUT; wire nor_a, nor_b;
    sky130_fd_sc_hd__nor3_1 u_nor_a(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.Y(nor_a));
    sky130_fd_sc_hd__nor3_1 u_nor_b(.A(DIN4|IN4|D),.B(DIN5|IN5|E),.C(DIN6|IN6|F),.Y(nor_b));
    sky130_fd_sc_hd__and2_1 u_and(.A(nor_a),.B(nor_b),.X(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd5s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E; output Q,QN,Y,X,OUT; wire and4_out;
    sky130_fd_sc_hd__and4_4 u_and4(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.X(and4_out));
    sky130_fd_sc_hd__nand2_4 u_nand2(.A(and4_out),.B(DIN5|IN5|E),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi222s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2; output Q,QN,Y,X,OUT; wire and_a, and_b, and_c;
    sky130_fd_sc_hd__and2_2 u_and_a(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(and_a));
    sky130_fd_sc_hd__and2_2 u_and_b(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.X(and_b));
    sky130_fd_sc_hd__and2_2 u_and_c(.A(DIN5|IN5|C1),.B(DIN6|IN6|C2),.X(and_c));
    sky130_fd_sc_hd__nor3_2 u_nor(.A(and_a),.B(and_b),.C(and_c),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd2s3(Q,QN,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and2s3(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and3s3(Q,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd3s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module or2s2(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module or2s3(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module i1s3(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_1 inst(.A(DIN|IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module ib1s9(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_1 inst(.A(DIN|IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module ib1s5(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_1 inst(.A(DIN|IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module dffs2(Q,QN,Y,X,OUT,DIN,IN1,CLK,CK);
    input DIN,IN1,CLK,CK; output Q,QN,Y,X,OUT; wire q_out;
    sky130_fd_sc_hd__dfxtp_1 dff_core(.CLK(CLK|CK),.D(DIN|IN1),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module nor2s2 (Q, DIN1, DIN2);
    output Q; input DIN1, DIN2;
    sky130_fd_sc_hd__nor2_1 inst (.Y(Q), .A(DIN1), .B(DIN2));
endmodule

module nor2s3(Q,QN,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nor5s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E; output Q,QN,Y,X,OUT; wire tmp;
    sky130_fd_sc_hd__nor4_1 u_nor4(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.Y(tmp));
    sky130_fd_sc_hd__nor2_1 u_nor2(.A(tmp),.B(DIN5|IN5|E),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module or5s3(Q,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A,B,C,D,E; output Q,Y,X,OUT; wire tmp;
    sky130_fd_sc_hd__or4_1 u_or4(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.X(tmp));
    sky130_fd_sc_hd__or2_1 u_or2(.A(tmp),.B(DIN5|IN5|E),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and4s2(Q,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and4_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module xnr2s1(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__xnor2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.Y(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module xor2s3(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__xor2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module or3s3(Q,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd4s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand4_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai32s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,A3,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,A3,B1,B2; output Q,QN,Y,X,OUT; wire or_s1, or_s2, and_s;
    sky130_fd_sc_hd__or3_1 or_stage1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.X(or_s1));
    sky130_fd_sc_hd__or2_1 or_stage2(.A(DIN4|IN4|B1),.B(DIN5|IN5|B2),.X(or_s2));
    sky130_fd_sc_hd__and2_1 and_stage(.A(or_s1),.B(or_s2),.X(and_s));
    sky130_fd_sc_hd__inv_1 final_inv(.A(and_s),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module xnr2s3(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__xnor2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.Y(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module sdffs1(Q,QN,Y,X,OUT,DIN,IN1,SDIN,SI,SCD,SSEL,SE,SCE,CLK,CK);
    input DIN,IN1,SDIN,SI,SCD,SSEL,SE,SCE,CLK,CK; output Q,QN,Y,X,OUT; wire next_d, q_out;
    sky130_fd_sc_hd__mux2_1 scan_mux(.A0(DIN|IN1),.A1(SDIN|SI|SCD),.S(SSEL|SE|SCE),.X(next_d));
    sky130_fd_sc_hd__dfxtp_1 dff_core(.CLK(CLK|CK),.D(next_d),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module dffles2(Q,QN,Y,X,OUT,DIN,IN1,EB,CLK,CK);
    input DIN,IN1,EB,CLK,CK; output Q,QN,Y,X,OUT; wire next_d, q_out;
    sky130_fd_sc_hd__mux2_1 hold_mux(.A0(DIN|IN1),.A1(q_out),.S(EB),.X(next_d));
    sky130_fd_sc_hd__dfxtp_1 dff_core(.CLK(CLK|CK),.D(next_d),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module mxi21s3(Q,QN,Y,X,OUT,DIN1,DIN2,SIN,IN1,IN2,S0,S);
    input DIN1,DIN2,SIN,IN1,IN2,S0,S; output Q,QN,Y,X,OUT; wire mux_out;
    sky130_fd_sc_hd__mux2_1 mux_core(.A0(DIN1|IN1),.A1(DIN2|IN2),.S(SIN|S0|S),.X(mux_out));
    sky130_fd_sc_hd__inv_1 inv_core(.A(mux_out),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module mx21s3(Q,QN,Y,X,OUT,DIN1,DIN2,SIN,IN1,IN2,S0,S);
    input DIN1,DIN2,SIN,IN1,IN2,S0,S; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__mux2_1 inst(.A0(DIN1|IN1),.A1(DIN2|IN2),.S(SIN|S0|S),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module mxi41s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1);
    input DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1; output Q,QN,Y,X,OUT; wire m1, m2, m3;
    sky130_fd_sc_hd__mux2_1 mux_a(.A0(DIN1|IN1),.A1(DIN2|IN2),.S(SIN0|S0),.X(m1));
    sky130_fd_sc_hd__mux2_1 mux_b(.A0(DIN3|IN3),.A1(DIN4|IN4),.S(SIN0|S0),.X(m2));
    sky130_fd_sc_hd__mux2_1 mux_c(.A0(m1),.A1(m2),.S(SIN1|S1),.X(m3));
    sky130_fd_sc_hd__inv_1 inv_q(.A(m3),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd2s2(Q,QN,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nnd3s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nand3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nor3s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module ib1s2(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_1 inst(.A(DIN|IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module xor2s2(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__xor2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module xnr2s2(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__xnor2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.Y(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai22s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,B2; output Q,QN,Y,X,OUT; wire or_a, or_b, and_out;
    sky130_fd_sc_hd__or2_1 g1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(or_a));
    sky130_fd_sc_hd__or2_1 g2(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.X(or_b));
    sky130_fd_sc_hd__and2_1 g3(.A(or_a),.B(or_b),.X(and_out));
    sky130_fd_sc_hd__inv_1 g4(.A(and_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai13s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,B1,B2,B3);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,B1,B2,B3; output Q,QN,Y,X,OUT; wire or_b, and_out;
    sky130_fd_sc_hd__or3_1 g1(.A(DIN2|IN2|B1),.B(DIN3|IN3|B2),.C(DIN4|IN4|B3),.X(or_b));
    sky130_fd_sc_hd__and2_1 g2(.A(DIN1|IN1|A1),.B(or_b),.X(and_out));
    sky130_fd_sc_hd__inv_1 g3(.A(and_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and2s2(Q,Y,X,OUT,DIN1,DIN2,IN1,IN2,A,B);
    input DIN1,DIN2,IN1,IN2,A,B; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and2_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module and3s2(Q,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,Y,X,OUT;
    sky130_fd_sc_hd__and3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module ib1s1(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_1 inst(.A(DIN|IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai211s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,C1);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,C1; output Q,QN,Y,X,OUT; wire or_out, and_partial;
    sky130_fd_sc_hd__or2_1 g1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(or_out));
    sky130_fd_sc_hd__and2_1 g2(.A(or_out),.B(DIN3|IN3|B1),.X(and_partial));
    sky130_fd_sc_hd__nand2_1 g3(.A(and_partial),.B(DIN4|IN4|C1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi21s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,A2,B1);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,A2,B1; output Q,QN,Y,X,OUT; wire and_out;
    sky130_fd_sc_hd__and2_1 g1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(and_out));
    sky130_fd_sc_hd__nor2_1 g2(.A(and_out),.B(DIN3|IN3|B1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi23s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,B3);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,B3; output Q,QN,Y,X,OUT; wire and_stage1, and_stage2, or_stage;
    sky130_fd_sc_hd__and2_1 g1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(and_stage1));
    sky130_fd_sc_hd__and3_1 g2(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.C(DIN5|IN5|B3),.X(and_stage2));
    sky130_fd_sc_hd__or2_1 g3(.A(and_stage1),.B(and_stage2),.X(or_stage));
    sky130_fd_sc_hd__inv_1 g4(.A(or_stage),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoai1112s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,A3,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,A3,B1,B2; output Q,QN,Y,X,OUT; wire and_stage2, or_stage;
    sky130_fd_sc_hd__and2_1 g1(.A(DIN4|IN4|B1),.B(DIN5|IN5|B2),.X(and_stage2));
    sky130_fd_sc_hd__or4_1  g2(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.D(and_stage2),.X(or_stage));
    sky130_fd_sc_hd__inv_1  g3(.A(or_stage),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai222s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,C1,C2; output Q,QN,Y,X,OUT; wire or_a, or_b, or_c, and_stage;
    sky130_fd_sc_hd__or2_1  g1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(or_a));
    sky130_fd_sc_hd__or2_1  g2(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.X(or_b));
    sky130_fd_sc_hd__or2_1  g3(.A(DIN5|IN5|C1),.B(DIN6|IN6|C2),.X(or_c));
    sky130_fd_sc_hd__and3_1 g4(.A(or_a),.B(or_b),.C(or_c),.X(and_stage));
    sky130_fd_sc_hd__inv_1  g5(.A(and_stage),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi22s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,B2; output Q,QN,Y,X,OUT; wire and_a, and_b, or_out;
    sky130_fd_sc_hd__and2_1 g1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(and_a));
    sky130_fd_sc_hd__and2_1 g2(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.X(and_b));
    sky130_fd_sc_hd__or2_1  g3(.A(and_a),.B(and_b),.X(or_out));
    sky130_fd_sc_hd__inv_1  g4(.A(or_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai321s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,B1,B2,C1);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,B1,B2,C1; output Q,QN,Y,X,OUT; wire or_stage1_out, or_stage2_out, and_stage_out;
    sky130_fd_sc_hd__or3_1  or_stage1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.X(or_stage1_out));
    sky130_fd_sc_hd__or2_1  or_stage2(.A(DIN4|IN4|B1),.B(DIN5|IN5|B2),.X(or_stage2_out));
    sky130_fd_sc_hd__and3_1 and_stage(.A(or_stage1_out),.B(or_stage2_out),.C(DIN6|IN6|C1),.X(and_stage_out));
    sky130_fd_sc_hd__inv_1  final_inv(.A(and_stage_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai33s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,B1,B2,B3);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,B1,B2,B3; output Q,QN,Y,X,OUT; wire or_stage1_out, or_stage2_out, and_stage_out;
    sky130_fd_sc_hd__or3_1  or_stage1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.X(or_stage1_out));
    sky130_fd_sc_hd__or3_1  or_stage2(.A(DIN4|IN4|B1),.B(DIN5|IN5|B2),.C(DIN6|IN6|B3),.X(or_stage2_out));
    sky130_fd_sc_hd__and2_1 and_stage(.A(or_stage1_out),.B(or_stage2_out),.X(and_stage_out));
    sky130_fd_sc_hd__inv_1  final_inv(.A(and_stage_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai1112s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,A3,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,A3,B1,B2; output Q,QN,Y,X,OUT; wire and_stage, or_stage;
    sky130_fd_sc_hd__and2_1 g1(.A(DIN4|IN4|B1),.B(DIN5|IN5|B2),.X(and_stage));
    sky130_fd_sc_hd__or4_1  g2(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.D(and_stage),.X(or_stage));
    sky130_fd_sc_hd__inv_1  g3(.A(or_stage),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai211s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,C1);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,C1; output Q,QN,Y,X,OUT; wire or_out, and_partial;
    sky130_fd_sc_hd__or2_1  g1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(or_out));
    sky130_fd_sc_hd__and2_1 g2(.A(or_out),.B(DIN3|IN3|B1),.X(and_partial));
    sky130_fd_sc_hd__nand2_1 g3(.A(and_partial),.B(DIN4|IN4|C1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module mxi21s2(Q,QN,Y,X,OUT,DIN1,DIN2,SIN,IN1,IN2,S0,S);
    input DIN1,DIN2,SIN,IN1,IN2,S0,S; output Q,QN,Y,X,OUT; wire mux_out;
    sky130_fd_sc_hd__mux2_1 mux_core(.A0(DIN1|IN1),.A1(DIN2|IN2),.S(SIN|S0|S),.X(mux_out));
    sky130_fd_sc_hd__inv_1 inv_core(.A(mux_out),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module mxi41s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1);
    input DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1; output Q,QN,Y,X,OUT; wire m1, m2, m3;
    sky130_fd_sc_hd__mux2_1 mux_stage1_a(.A0(DIN1|IN1),.A1(DIN2|IN2),.S(SIN0|S0),.X(m1));
    sky130_fd_sc_hd__mux2_1 mux_stage1_b(.A0(DIN3|IN3),.A1(DIN4|IN4),.S(SIN0|S0),.X(m2));
    sky130_fd_sc_hd__mux2_1 mux_stage2(.A0(m1),.A1(m2),.S(SIN1|S1),.X(m3));
    sky130_fd_sc_hd__inv_1  final_inv(.A(m3),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module mx41s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1);
    input DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1; output Q,QN,Y,X,OUT; wire m1, m2;
    sky130_fd_sc_hd__mux2_1 mux_stage1_a(.A0(DIN1|IN1),.A1(DIN2|IN2),.S(SIN0|S0),.X(m1));
    sky130_fd_sc_hd__mux2_1 mux_stage1_b(.A0(DIN3|IN3),.A1(DIN4|IN4),.S(SIN0|S0),.X(m2));
    sky130_fd_sc_hd__mux2_1 mux_stage2(.A0(m1),.A1(m2),.S(SIN1|S1),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi13s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,B1,B2,B3);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,B1,B2,B3; output Q,QN,Y,X,OUT; wire and_stage_out, or_stage_out;
    sky130_fd_sc_hd__and3_1 and_stage(.A(DIN2|IN2|B1),.B(DIN3|IN3|B2),.C(DIN4|IN4|B3),.X(and_stage_out));
    sky130_fd_sc_hd__or2_1  or_stage(.A(DIN1|IN1|A1),.B(and_stage_out),.X(or_stage_out));
    sky130_fd_sc_hd__inv_1  final_inv(.A(or_stage_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai21s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,A2,B1);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,A2,B1; output Q,QN,Y,X,OUT; wire or_stage_out;
    sky130_fd_sc_hd__or2_1  or_stage(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(or_stage_out));
    sky130_fd_sc_hd__nand2_1 final_nand(.A(or_stage_out),.B(DIN3|IN3|B1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module or4s3(Q,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D; output Q,Y,X,OUT;
    sky130_fd_sc_hd__or4_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.X(Q));
    assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai1112s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,A3,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,A3,B1,B2; output Q,QN,Y,X,OUT; wire and_stage_out, or_stage_out;
    sky130_fd_sc_hd__and2_1 nested_and(.A(DIN4|IN4|B1),.B(DIN5|IN5|B2),.X(and_stage_out));
    sky130_fd_sc_hd__or4_1  wide_or(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.D(and_stage_out),.X(or_stage_out));
    sky130_fd_sc_hd__inv_1  final_inv(.A(or_stage_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module mx41s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1);
    input DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1; output Q,QN,Y,X,OUT; wire m1, m2;
    sky130_fd_sc_hd__mux2_1 mux_stage1_a(.A0(DIN1|IN1),.A1(DIN2|IN2),.S(SIN0|S0),.X(m1));
    sky130_fd_sc_hd__mux2_1 mux_stage1_b(.A0(DIN3|IN3),.A1(DIN4|IN4),.S(SIN0|S0),.X(m2));
    sky130_fd_sc_hd__mux2_1 mux_stage2(.A0(m1),.A1(m2),.S(SIN1|S1),.X(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai322s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,DIN7,IN1,IN2,IN3,IN4,IN5,IN6,IN7,A1,A2,A3,B1,B2,C1,C2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,DIN7,IN1,IN2,IN3,IN4,IN5,IN6,IN7,A1,A2,A3,B1,B2,C1,C2; output Q,QN,Y,X,OUT; wire or_stage1_out, or_stage2_out, or_stage3_out, and_stage_out;
    sky130_fd_sc_hd__or3_1  or_stage1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.X(or_stage1_out));
    sky130_fd_sc_hd__or2_1  or_stage2(.A(DIN4|IN4|B1),.B(DIN5|IN5|B2),.X(or_stage2_out));
    sky130_fd_sc_hd__or2_1  or_stage3(.A(DIN6|IN6|C1),.B(DIN7|IN7|C2),.X(or_stage3_out));
    sky130_fd_sc_hd__and3_1 and_stage(.A(or_stage1_out),.B(or_stage2_out),.C(or_stage3_out),.X(and_stage_out));
    sky130_fd_sc_hd__inv_1  final_inv(.A(and_stage_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoai122s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,B1,B2,C1,C2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,B1,B2,C1,C2; output Q,QN,Y,X,OUT; wire or_stage1_out, or_stage2_out, and_stage_out;
    sky130_fd_sc_hd__or2_1  or_stage1(.A(DIN2|IN2|B1),.B(DIN3|IN3|B2),.X(or_stage1_out));
    sky130_fd_sc_hd__or2_1  or_stage2(.A(DIN4|IN4|C1),.B(DIN5|IN5|C2),.X(or_stage2_out));
    sky130_fd_sc_hd__and3_1 and_stage(.A(DIN1|IN1|A1),.B(or_stage1_out),.C(or_stage2_out),.X(and_stage_out));
    sky130_fd_sc_hd__inv_1  final_inv(.A(and_stage_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai221s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1; output Q,QN,Y,X,OUT; wire or_stage1_out, or_stage2_out, and_stage_out;
    sky130_fd_sc_hd__or2_1  or_stage1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(or_stage1_out));
    sky130_fd_sc_hd__or2_1  or_stage2(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.X(or_stage2_out));
    sky130_fd_sc_hd__and3_1 and_stage(.A(or_stage1_out),.B(or_stage2_out),.C(DIN5|IN5|C1),.X(and_stage_out));
    sky130_fd_sc_hd__inv_1  final_inv(.A(and_stage_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module i1s12(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_1 inst(.A(DIN|IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nor4s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A,B,C,D; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor4_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.D(DIN4|IN4|D),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nor6s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A,B,C,D,E,F);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A,B,C,D,E,F; output Q,QN,Y,X,OUT; wire tmp1, tmp2;
    sky130_fd_sc_hd__nor3_1 u_nor3_a(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.Y(tmp1));
    sky130_fd_sc_hd__nor3_1 u_nor3_b(.A(DIN4|IN4|D),.B(DIN5|IN5|E),.C(DIN6|IN6|F),.Y(tmp2));
    sky130_fd_sc_hd__and2_1 u_and_comb(.A(tmp1),.B(tmp2),.X(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module nor3s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A,B,C; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__nor3_1 inst(.A(DIN1|IN1|A),.B(DIN2|IN2|B),.C(DIN3|IN3|C),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi221s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1);
    input DIN1,DIN2,DIN3,DIN4,DIN5,IN1,IN2,IN3,IN4,IN5,A1,A2,B1,B2,C1; output Q,QN,Y,X,OUT; wire and_stage1_out, and_stage2_out, or_stage_out;
    sky130_fd_sc_hd__and2_1 and_stage1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(and_stage1_out));
    sky130_fd_sc_hd__and2_1 and_stage2(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.X(and_stage2_out));
    sky130_fd_sc_hd__or3_1  or_stage(.A(and_stage1_out),.B(and_stage2_out),.C(DIN5|IN5|C1),.X(or_stage_out));
    sky130_fd_sc_hd__inv_1  final_inv(.A(or_stage_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module dsmxc31s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,SIN0,SIN1,CLK,IN1,IN2,IN3,S0,S1,CK);
    input DIN1,DIN2,DIN3,SIN0,SIN1,CLK,IN1,IN2,IN3,S0,S1,CK; output Q,QN,Y,X,OUT; wire m1_out, m2_out, q_out;
    sky130_fd_sc_hd__mux2_1 mux_stage1(.A0(DIN1|IN1),.A1(DIN2|IN2),.S(SIN0|S0),.X(m1_out));
    sky130_fd_sc_hd__mux2_1 mux_stage2(.A0(m1_out),.A1(DIN3|IN3),.S(SIN1|S1),.X(m2_out));
    sky130_fd_sc_hd__dfxtp_1 dff_core(.CLK(CLK|CK),.D(m2_out),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module oai21s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,A2,B1);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,A2,B1; output Q,QN,Y,X,OUT; wire or_stage_out;
    sky130_fd_sc_hd__or2_1 or_stage(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(or_stage_out));
    sky130_fd_sc_hd__nand2_1 final_nand(.A(or_stage_out),.B(DIN3|IN3|B1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai22s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,B2; output Q,QN,Y,X,OUT; wire or_stage1_out, or_stage2_out, and_stage_out;
    sky130_fd_sc_hd__or2_1 or_stage1(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(or_stage1_out));
    sky130_fd_sc_hd__or2_1 or_stage2(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.X(or_stage2_out));
    sky130_fd_sc_hd__and2_1 and_stage(.A(or_stage1_out),.B(or_stage2_out),.X(and_stage_out));
    sky130_fd_sc_hd__inv_1 final_inv(.A(and_stage_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi42s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,A4,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,A4,B1,B2; output Q,QN,Y,X,OUT; wire and4_out, and2_out;
    sky130_fd_sc_hd__and4_2 u_and4(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.D(DIN4|IN4|A4),.X(and4_out));
    sky130_fd_sc_hd__and2_2 u_and2(.A(DIN5|IN5|B1),.B(DIN6|IN6|B2),.X(and2_out));
    sky130_fd_sc_hd__nor2_2 u_nor2(.A(and4_out),.B(and2_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module dffcs2(Q,QN,Y,X,OUT,DIN,IN1,CLRB,RESET_B,CLK,CK);
    input DIN,IN1,CLRB,RESET_B,CLK,CK; output Q,QN,Y,X,OUT; wire q_out;
    sky130_fd_sc_hd__dfrtp_2 inst(.CLK(CLK|CK),.D(DIN|IN1),.RESET_B(CLRB|RESET_B),.Q(q_out));
    assign Q=q_out; assign QN=~q_out; assign Y=q_out; assign X=q_out; assign OUT=q_out;
endmodule

module aoi211s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,C1);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,C1; output Q,QN,Y,X,OUT; wire and_out;
    sky130_fd_sc_hd__and2_2 u_and(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(and_out));
    sky130_fd_sc_hd__nor3_2 u_nor(.A(and_out),.B(DIN3|IN3|B1),.C(DIN4|IN4|C1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi22s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,B2; output Q,QN,Y,X,OUT; wire and_a, and_b;
    sky130_fd_sc_hd__and2_2 u_and_a(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(and_a));
    sky130_fd_sc_hd__and2_2 u_and_b(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.X(and_b));
    sky130_fd_sc_hd__nor2_2 u_nor(.A(and_a),.B(and_b),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi123s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,B1,B2,C1,C2,C3);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,B1,B2,C1,C2,C3; output Q,QN,Y,X,OUT; wire and2_out, and3_out;
    sky130_fd_sc_hd__and2_2 u_and2(.A(DIN2|IN2|B1),.B(DIN3|IN3|B2),.X(and2_out));
    sky130_fd_sc_hd__and3_2 u_and3(.A(DIN4|IN4|C1),.B(DIN5|IN5|C2),.C(DIN6|IN6|C3),.X(and3_out));
    sky130_fd_sc_hd__nor3_2 u_nor3(.A(DIN1|IN1|A1),.B(and2_out),.C(and3_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module mxi21s1(Q,QN,Y,X,OUT,DIN1,DIN2,SIN,IN1,IN2,S0,S);
    input DIN1,DIN2,SIN,IN1,IN2,S0,S; output Q,QN,Y,X,OUT; wire mux_out;
    sky130_fd_sc_hd__mux2_1 u_mux(.A0(DIN1|IN1),.A1(DIN2|IN2),.S(SIN|S0|S),.X(mux_out));
    sky130_fd_sc_hd__inv_1 u_inv(.A(mux_out),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai24s3(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,B3,B4);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,B1,B2,B3,B4; output Q,QN,Y,X,OUT; wire or2_out, or4_out;
    sky130_fd_sc_hd__or2_4 u_or2(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(or2_out));
    sky130_fd_sc_hd__or4_4 u_or4(.A(DIN3|IN3|B1),.B(DIN4|IN4|B2),.C(DIN5|IN5|B3),.D(DIN6|IN6|B4),.X(or4_out));
    sky130_fd_sc_hd__nand2_4 u_nand(.A(or2_out),.B(or4_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi13s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,B1,B2,B3);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,B1,B2,B3; output Q,QN,Y,X,OUT; wire and3_out;
    sky130_fd_sc_hd__and3_2 u_and3(.A(DIN2|IN2|B1),.B(DIN3|IN3|B2),.C(DIN4|IN4|B3),.X(and3_out));
    sky130_fd_sc_hd__nor2_2 u_nor2(.A(DIN1|IN1|A1),.B(and3_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi42s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,A4,B1,B2);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,A4,B1,B2; output Q,QN,Y,X,OUT; wire and4_out, and2_out;
    sky130_fd_sc_hd__and4_1 u_and4(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.D(DIN4|IN4|A4),.X(and4_out));
    sky130_fd_sc_hd__and2_1 u_and2(.A(DIN5|IN5|B1),.B(DIN6|IN6|B2),.X(and2_out));
    sky130_fd_sc_hd__nor2_1 u_nor2(.A(and4_out),.B(and2_out),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi211s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,C1);
    input DIN1,DIN2,DIN3,DIN4,IN1,IN2,IN3,IN4,A1,A2,B1,C1; output Q,QN,Y,X,OUT; wire and2_out;
    sky130_fd_sc_hd__and2_1 u_and2(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(and2_out));
    sky130_fd_sc_hd__nor3_1 u_nor3(.A(and2_out),.B(DIN3|IN3|B1),.C(DIN4|IN4|C1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi33s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,B1,B2,B3);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,B1,B2,B3; output Q,QN,Y,X,OUT; wire and3_a, and3_b;
    sky130_fd_sc_hd__and3_2 u_and_a(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.X(and3_a));
    sky130_fd_sc_hd__and3_2 u_and_b(.A(DIN4|IN4|B1),.B(DIN5|IN5|B2),.C(DIN6|IN6|B3),.X(and3_b));
    sky130_fd_sc_hd__nor2_2 u_nor2(.A(and3_a),.B(and3_b),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module oai33s1(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,B1,B2,B3);
    input DIN1,DIN2,DIN3,DIN4,DIN5,DIN6,IN1,IN2,IN3,IN4,IN5,IN6,A1,A2,A3,B1,B2,B3; output Q,QN,Y,X,OUT; wire or3_a, or3_b;
    sky130_fd_sc_hd__or3_1 u_or_a(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.C(DIN3|IN3|A3),.X(or3_a));
    sky130_fd_sc_hd__or3_1 u_or_b(.A(DIN4|IN4|B1),.B(DIN5|IN5|B2),.C(DIN6|IN6|B3),.X(or3_b));
    sky130_fd_sc_hd__nand2_1 u_nand2(.A(or3_a),.B(or3_b),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module aoi21s2(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,A2,B1);
    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,A2,B1; output Q,QN,Y,X,OUT; wire and2_out;
    sky130_fd_sc_hd__and2_2 u_and2(.A(DIN1|IN1|A1),.B(DIN2|IN2|A2),.X(and2_out));
    sky130_fd_sc_hd__nor2_2 u_nor2(.A(and2_out),.B(DIN3|IN3|B1),.Y(Q));
    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule

module i1s11(Q,QN,Y,X,OUT,DIN,IN1,IN,A);
    input DIN,IN1,IN,A; output Q,QN,Y,X,OUT;
    sky130_fd_sc_hd__inv_8 inst(.A(DIN|IN1|IN|A),.Y(Q));
    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;
endmodule
