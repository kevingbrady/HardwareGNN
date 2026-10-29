import re

class ModuleTranslator:
    def __init__(self):
        self.discovered_macros = set()

        self.instance_pattern = re.compile(
            r'\\?([a-zA-Z_][a-zA-Z0-9_]*)\s+\\?[a-zA-Z_][a-zA-Z0-9_/\[\]]*\s*\(',
            re.DOTALL
        )

        self.keywords = {
            "module", "endmodule", "always", "initial", "assign", "wire", "reg",
            "input", "output", "inout", "is", "or", "and", "not", "xor", "xnor", "buf",
            "begin", "end", "if", "else", "case", "endcase", "generate", "endgenerate",
            "integer", "parameter", "localparam", "real", "time", "defparam",
            "ifdef", "ifndef", "else", "endif", "elsif", "include", "define", "undef",
            "tri", "tri0", "tri1", "supply0", "supply1", "wand", "wor", "trireg",
            "default", "posedge", "negedge", "forever", "repeat", "while", "for",
            "specparam", "specify", "endspecify", "table", "endtable", "primitive",
            "endprimitive", "signed", "unsigned", "scalared", "vectored", "small",
            "uart", "rs232", "transmitter", "receiver", "baud", "fifo", "top", "test"
        }

    def write_macro_definitions(self, verilog_file_list, output_path):
        self.discovered_macros.clear()

        for file in verilog_file_list:
            self.parse_file(file)

        generated_blocks = []
        # Track uniquely generated module names to enforce single-definition structures
        emitted_names = set()

        for instance in sorted(self.discovered_macros):
            base_name = instance.lstrip('\\').strip()

            # Enforce case-insensitive uniqueness filters
            if base_name.lower() in emitted_names:
                continue

            code_block = self._generate_module_code(base_name)
            if code_block and code_block.strip():
                generated_blocks.append(code_block.strip())
                emitted_names.add(base_name.lower())

        with open(output_path, "w") as f:
            f.write(
                '// Procedurally Generated Self-Contained Behavioral Module Definitions for Yosys Trojan Analysis\n')
            f.write(f'// Total macro blocks generated: {len(generated_blocks)}\n\n')
            f.write("\n\n".join(generated_blocks))
            f.write("\n")

    def parse_file(self, input_path):
        sanitized_lines = []
        with open(input_path, 'r') as f:
            for line in f:
                line_clean = re.sub(r'//.*', '', line)
                sanitized_lines.append(line_clean)

        content = "".join(sanitized_lines)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        matches = self.instance_pattern.findall(content)
        for cell_type in matches:
            cell_type_clean = cell_type.strip()
            check_name = cell_type_clean.lstrip('\\').lower()

            if check_name in self.keywords or check_name.startswith("sky130_"):
                continue

            if not re.match(r'^[a-zA-Z_]', check_name):
                continue

            self.discovered_macros.add(cell_type_clean)

    def _decode_instance_name(self, name):
        name_clean = name.lstrip('\\').lower()
        core = re.sub(r'_(asap7|sky130|sc|fd|hd|lp).*$', '', name_clean)
        if not core:
            core = name_clean

        raw_list = [
            "sdffsr", "sdffar", "sdffs", "dffles", "lsdnen", "isoland", "dffar", "sdff",
            "dffn", "dffc", "dffle", "lsdn", "hadd", "fadd", "nbuff", "maji", "inv",
            "buf", "nand", "nnd", "and", "nor", "xor", "xnor", "xnr", "mux", "mxi",
            "maj", "dff", "hb", "nb", "ib", "hi", "fadd", "hadd", "fa", "ha", "oa",
            "ao", "oai", "aoi", "iso", "lar", "or", "i"
        ]
        sorted_prefixes = sorted(raw_list, key=len, reverse=True)

        matched_prefix = None
        for prefix in sorted_prefixes:
            if core.startswith(prefix):
                matched_prefix = prefix
                break

        if not matched_prefix:
            return None

        remaining = core[len(matched_prefix):]
        digit_match = re.match(r'^(\d+)', remaining)

        if digit_match:
            digit_str = digit_match.group(1)
            digits_val = [int(d) for d in digit_str] if len(digit_str) > 1 else int(digit_str)
        else:
            digits_val = 1

        return {"type": matched_prefix.lower(), "digits": digits_val}

    def _generate_module_code(self, instance_name):
        instance_info = self._decode_instance_name(instance_name)
        if not instance_info:
            return f"// Warning: Could not decode structural prefix for cell '{instance_name}'"

        t = instance_info["type"]
        digits = instance_info["digits"]
        lines = []

        std_assigns = "    assign QN=Q; assign Y=Q; assign X=Q; assign OUT=Q;"
        inv_assigns = "    assign QN=~Q; assign Y=Q; assign X=Q; assign OUT=Q;"

        module_header_name = f"{instance_name} " if instance_name.startswith('\\') else instance_name

        # --------------------------------------------------------------------------
        # 1. INVERTERS & BUFFERS (Fixed ib1s5, hi1s1, i1s12 module naming bugs)
        # --------------------------------------------------------------------------
        if t in ["i", "inv", "ib", "hi", "buf", "nbuff", "hb", "nb"]:
            is_inv = t in ["i", "inv", "ib", "hi"]

            # Universal port signature mapping to accommodate any erratic netlist pin wires
            lines.append(f"module {module_header_name}(Q,QN,Y,X,OUT,ZN,DIN,IN1,IN,INP,PIN_A);")
            lines.append("    input DIN,IN1,IN,INP,PIN_A; output Q,QN,Y,X,OUT,ZN;")
            lines.append("    wire _w_in_ = DIN | IN1 | IN | INP | PIN_A;")
            lines.append(f"    assign Q = {'~_w_in_' if is_inv else '_w_in_'};")
            lines.append("    assign QN = ~Q; assign Y = Q; assign X = Q; assign OUT = Q; assign ZN = Q;")

        # --------------------------------------------------------------------------
        # 2. COMBINATIONAL PRIMITIVES (AND, NAND, OR, NOR, XOR, XNOR)
        # --------------------------------------------------------------------------
        elif t in ["and", "nand", "nnd", "or", "nor", "xor", "xnor", "xnr"]:
            size = digits if isinstance(digits, int) else (digits[0] if isinstance(digits, list) else 2)

            din = [f"DIN{i + 1}" for i in range(size)]
            in_p = [f"IN{i + 1}" for i in range(size)]
            abc = [chr(ord('A') + i) for i in range(size)]
            inputs = din + in_p + abc

            has_qn = t in ["nand", "nnd", "nor", "xnor", "xnr"]
            outputs = ["Q", "QN", "Y", "X", "OUT"] if has_qn else ["Q", "Y", "X", "OUT"]

            lines.append(f"module {module_header_name}({','.join(outputs + inputs)});")
            lines.append(f"    input {','.join(inputs)}; output {','.join(outputs)};")

            operand = " & " if "and" in t or "nnd" in t else (" | " if "or" in t or "nor" in t else " ^ ")
            logic_expr = operand.join([f"({din[i]}|{in_p[i]}|{abc[i]})" for i in range(size)])

            lines.append(f"    wire raw_func = {logic_expr};")
            lines.append(f"    assign Q = {'~raw_func' if has_qn else 'raw_func'};")
            lines.append(std_assigns if has_qn else "    assign Y=Q; assign X=Q; assign OUT=Q;")

        # --------------------------------------------------------------------------
        # 3. COMPLEX AND-OR / OR-AND COMBINATIONS (aoi, oai, ao, oa, aoai)
        # --------------------------------------------------------------------------
        elif t in ["aoi", "oai", "ao", "oa", "aoai"]:
            if isinstance(digits, int):
                digits_list = [int(d) for d in str(digits)]
            elif isinstance(digits, list):
                digits_list = digits
            else:
                digits_list = [2, 1]  # Standard operational functional fallback

            total_in = sum(digits_list)

            din = [f"DIN{i + 1}" for i in range(total_in)]
            in_p = [f"IN{i + 1}" for i in range(total_in)]

            # Formulate legal, pure-text alphanumeric port signals for the module wrapper
            abc = []
            abc_char = ord('A')
            for group in digits_list:
                for k in range(group):
                    abc.append(f"{chr(abc_char)}{k + 1}" if group > 1 else f"{chr(abc_char)}1")
                abc_char += 1

            inputs = din + in_p + abc
            has_qn = t in ["aoi", "oai", "aoai"]
            outputs = ["Q", "QN", "Y", "X", "OUT"] if has_qn else ["Q", "Y", "X", "OUT"]

            lines.append(f"module {module_header_name}({','.join(outputs + inputs)});")
            lines.append(f"    input {','.join(inputs)}; output {','.join(outputs)};")

            is_oai = "oai" in t or t == "oa"
            inner_op = " | " if is_oai else " & "
            outer_op = " & " if is_oai else " | "

            group_exprs = []
            g_idx = 0
            for num in digits_list:
                terms = [f"({din[g_idx + k]}|{in_p[g_idx + k]}|{abc[g_idx + k]})" for k in range(num)]
                group_exprs.append(f"({inner_op.join(terms)})")
                g_idx += num

            lines.append(f"    wire raw_comb = {outer_op.join(group_exprs)};")
            lines.append(f"    assign Q = {'~raw_comb' if has_qn else 'raw_comb'};")
            lines.append(inv_assigns if has_qn else std_assigns)

        # --------------------------------------------------------------------------
        # 4. MULTIPLEXERS (Mux / Inverting Mux)
        # --------------------------------------------------------------------------
        elif t in ["mx", "mux", "mxi"]:
            size = digits if isinstance(digits, int) else 2
            is_inverted = t == "mxi"

            if size == 4:
                lines.append(
                    f"module {module_header_name}(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1);")
                lines.append("    input DIN1,DIN2,DIN3,DIN4,SIN0,SIN1,IN1,IN2,IN3,IN4,S0,S1; output Q,QN,Y,X,OUT;")
                lines.append("    wire m1 = (SIN0|S0) ? (DIN2|IN2) : (DIN1|IN1);")
                lines.append("    wire m2 = (SIN0|S0) ? (DIN4|IN4) : (DIN3|IN3);")
                lines.append(f"    assign Q = {'~' if is_inverted else ''}((SIN1|S1) ? m2 : m1);")
            else:
                lines.append(f"module {module_header_name}(Q,QN,Y,X,OUT,IN1,IN2,SIN,IN1_alt,IN2_alt,S0,S);")
                lines.append("    input IN1,IN2,SIN,IN1_alt,IN2_alt,S0,S; output Q,QN,Y,X,OUT;")
                lines.append(
                    f"    assign Q = {'~' if is_inverted else ''}((SIN|S0|S) ? (IN2|IN2_alt) : (IN1|IN1_alt));")

            lines.append(inv_assigns if is_inverted else std_assigns)

        # --------------------------------------------------------------------------
        # 5. SEQUENTIAL REGISTER CELLS, LATCHES, & SPECIAL BLOCKS
        # --------------------------------------------------------------------------
        elif t in ["dff", "sdff", "sdffsr", "sdffar", "sdffs", "dffar", "dffn", "dffc", "dffle", "lsdnen", "lsdn",
                   "lar", "isoland", "iso"]:
            lines.append(
                f"module {instance_name}(CLK,CK,D,DIN,IN1,SDIN,SI,SCD,SSEL,SE,SCE,SET,SETB,RESET,RST,RN,SN,Q,QN,Y,X,OUT,IN2,IN3,A,B,C,EN,ENA,ISO,ISOLN,ENB,GATE_N,GATE,RSTB,RESET_B);")
            lines.append(
                "    input CLK,CK,D,DIN,IN1,SDIN,SI,SCD,SSEL,SE,SCE,SET,SETB,RESET,RST,RN,SN,IN2,IN3,A,B,C,EN,ENA,ISO,ISOLN,ENB,GATE_N,GATE,RSTB,RESET_B; output reg Q; output QN,Y,X,OUT;")

            lines.append("    wire _clk_   = CLK | CK;")
            lines.append("    wire _d_     = D | DIN | IN1 | A;")

            # FIXED: Blended active-low SETB net (~SETB) straight into the asynchronous trigger net
            lines.append("    wire _async_ = RESET | RST | SET | ~SETB | ~RN | ~SN | ~(RSTB | RESET_B);")

            if t in ["isoland", "iso"]:
                lines.append("    wire _ctrl_ = EN | ENA | ISO | (~ISOLN);")
                lines.append("    always @(*) begin Q = _d_ & _ctrl_; end")
            elif t in ["lsdnen", "lsdn", "lar"]:
                if t == "lar":
                    lines.append("    wire _gate_ = (CLK | GATE | ~ENB | ~GATE_N);")
                else:
                    lines.append("    wire _gate_ = ~(ENB | GATE_N | ~CLK | ~GATE);")
                lines.append("    always @(*) begin if (_async_) Q = 1'b0; else if (_gate_) Q = _d_; end")
            else:
                is_scan = t in ["sdff", "sdffsr", "sdffar", "sdffs"]
                # Include asynchronous set variants alongside resets to capture async flip-flop behavior
                has_async = t in ["dffar", "sdffar", "sdffsr",
                                  "sdffs"] or "asx" in instance_name.lower() or "set" in instance_name.lower()

                lines.append(f"    wire _d_mux_ = {'((SSEL|SE|SCE) ? (SDIN|SI|SCD) : _d_)' if is_scan else '_d_'};")
                lines.append(f"    wire _trig_clk_ = {'~_clk_' if t == 'dffn' else '_clk_'};")

                if has_async:
                    # For a preset-heavy cell like DFFASX1, if an async trigger fires, force it high or low dynamically
                    lines.append("    always @(posedge _trig_clk_ or posedge _async_) begin")
                    lines.append("        if (_async_) Q <= (SET | ~SETB) ? 1'b1 : 1'b0;")
                    lines.append("        else         Q <= _d_mux_;")
                    lines.append("    end")
                else:
                    lines.append("    always @(posedge _trig_clk_) begin Q <= _d_mux_; end")

            lines.append(inv_assigns)

        # --------------------------------------------------------------------------
        # 6 ARITHMETIC FULL/HALF ADDERS & MAJORITY GATES (fa, fadd, ha, hadd, maj, maji)
        # --------------------------------------------------------------------------
        elif t in ["fa", "fadd", "ha", "hadd", "maj", "maji"]:
            if "maj" in t:
                lines.append(f"module {module_header_name}(Q,QN,Y,X,OUT,DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,B1,C1,A,B,C);")
                lines.append("    input DIN1,DIN2,DIN3,IN1,IN2,IN3,A1,B1,C1,A,B,C; output Q,QN,Y,X,OUT;")
                lines.append(
                    "    wire a = DIN1 | IN1 | A1 | A; wire b = DIN2 | IN2 | B1 | B; wire c = DIN3 | IN3 | C1 | C;")
                lines.append("    assign Q = (a & b) | (b & c) | (a & c);")
                lines.append("    assign QN = ~Q; assign Y = Q; assign X = Q; assign OUT = Q;")
            else:
                is_full = t in ["fa", "fadd"]
                # Expanded arithmetic mapping supporting standard, inverted, and tool-specific complements
                lines.append(f"module {module_header_name}(S,SUM,SO,SUM_alt,SN,SON,CO,COUT,CON,C1,A,B,CI,CIN,A0,B0);")
                lines.append(
                    "    input A,B,CI,CIN,A0,B0; output S,SUM,SO,SUM_alt,SN,SON,CO,COUT,CON,C1; wire s_out, c_out;")
                lines.append("    wire _a_ = A | A0; wire _b_ = B | B0; wire _cin_ = CI | CIN;")

                if is_full:
                    lines.append("    assign s_out = _a_ ^ _b_ ^ _cin_;")
                    lines.append("    assign c_out = (_a_ & _b_) | (_b_ & _cin_) | (_a_ & _cin_);")
                else:
                    lines.append("    assign s_out = _a_ ^ _b_;")
                    lines.append("    assign c_out = _a_ & _b_;")

                # Broad output assignment routing to safely map any synthesis tool pin expectations
                lines.append(
                    "    assign S = s_out; assign SUM = s_out; assign SO = s_out; assign SUM_alt = s_out; assign SN = ~s_out; assign SON = ~s_out;")
                lines.append("    assign CO = c_out; assign COUT = c_out; assign C1 = c_out; assign CON = ~c_out;")

        # ==========================================================================
        # UNIFIED TERMINAL CLOSURE HOOK
        # ==========================================================================
        # Ensures every module block is wrapped with exactly one endmodule statement
        if lines:
            lines.append("endmodule")
            return "\n".join(lines)
        return ""