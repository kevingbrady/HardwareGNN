

'''
# 2. Extract bases and numerical pins
parsed_data = [parse_verilog_port(p) for p in verilog_ports]
base_names = [item[0] for item in parsed_data]

# Print check to verify parsing behavior:
# "CLK_IN"       -> Base: "CLK_IN",       Index: -1.0
# "DATA_BUS_IN_0" -> Base: "DATA_BUS_IN", Index: 0.0
# "DIN_1"        -> Base: "DIN",        Index: 1.0

# 3. Create compact text embeddings (e.g., 8 dimensions)
unique_bases = sorted(list(set(base_names)))
base_to_id = {name: idx for idx, name in enumerate(unique_bases)}

TARGET_DIM = 8  # Keep it small to avoid overwhelming your graph size
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
raw_text_vectors = model.encode(unique_bases, convert_to_tensor=True, truncate_dim=TARGET_DIM)

# 4. Helper function to process edge lists into tensors
edge_src_ports = ["DIN_1", "CLK_IN", "DATA_BUS_IN_0"]  # Sample source ports
edge_dst_ports = ["DIN_2", "CLK_OUT", "RESET_N"]       # Sample destination ports

def prepare_edge_side_tensors(raw_edge_ports):
    base_ids = []
    indices = []
    for port in raw_edge_ports:
        base, idx = parse_verilog_port(port)
        base_ids.append(base_to_id[base])
        indices.append(idx)
    
    return (
        torch.tensor(base_ids, dtype=torch.long),
        torch.tensor(indices, dtype=torch.float32).unsqueeze(-1)  # Shape: [num_edges, 1]
    )

src_base_ids, src_pin_indices = prepare_edge_side_tensors(edge_src_ports)
dst_base_ids, dst_pin_indices = prepare_edge_side_tensors(edge_dst_ports)

# 5. Initialize trainable embedding layers (8 text dims)
src_emb_layer = nn.Embedding.from_pretrained(raw_text_vectors, freeze=False)
dst_emb_layer = nn.Embedding.from_pretrained(raw_text_vectors, freeze=False)

# 6. Assemble your final ultra-lean edge features
src_vectors = src_emb_layer(src_base_ids)  # [num_edges, 8]
dst_vectors = dst_emb_layer(dst_base_ids)  # [num_edges, 8]

# Concat index bit to each side -> 9 dims per side
src_features = torch.cat([src_vectors, src_pin_indices], dim=-1)  # [num_edges, 9]
dst_features = torch.cat([dst_vectors, dst_pin_indices], dim=-1)  # [num_edges, 9]

# Combined final tensor for PyG
edge_attr = torch.cat([src_features, dst_features], dim=-1)  # [num_edges, 18]

print("Final edge attribute tensor shape:", edge_attr.shape)
'''



