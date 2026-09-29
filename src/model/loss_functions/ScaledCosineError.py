import torch


class ScaledCosineError(torch.nn.Module):
    def __init__(self, alpha=1.5, mse_weight=0.1):
        super().__init__()
        self.alpha = alpha
        self.mse_weight = mse_weight

    def forward(self, pred, target):
        # 1. Secure normalization
        pred_norm = torch.nn.functional.normalize(pred, p=2, dim=-1)
        target_norm = torch.nn.functional.normalize(target, p=2, dim=-1)

        # 2. Per-element error calculation (Keeps node dimension intact)
        cosine_sim = torch.clamp((pred_norm * target_norm).sum(dim=-1), min=-0.9999, max=0.9999)
        sce_loss = (1.0 - cosine_sim) ** self.alpha
        mse_loss = ((pred_norm - target_norm) ** 2).mean(dim=-1)

        loss = sce_loss + (self.mse_weight * mse_loss)

        return loss


