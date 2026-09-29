import torch
from torch.nn import Module, functional


class FocalLoss(Module):
    def __init__(self, alpha=0.75, gamma=2.0, reduction='mean', device=None):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        # Keep device purely as an optional fallback; prefer dynamic inference
        self.device = device

    def forward(self, inputs, targets):
        # Force high-precision FP32 computation to completely prevent low-precision underflow
        with torch.amp.autocast(device_type='cuda', enabled=False):
            # Dynamic device matching avoids explicit device syncing loops
            current_device = inputs.device
            inputs = inputs.float()

            # Determine task type explicitly by checking the target's shape relative to inputs
            # Multiclass targets are 1D categorical arrays [N], while binary targets share shape with inputs
            is_binary = (inputs.dim() == 1) or (inputs.shape == targets.shape)

            if is_binary:
                inputs = inputs.view(-1)
                targets = targets.to(device=current_device, dtype=inputs.dtype).view(-1)

                # Stably calculate base Binary Cross Entropy
                base_loss = functional.binary_cross_entropy_with_logits(
                    inputs, targets, reduction='none'
                )
                # Derive class balancing factor dynamically
                alpha_factor = torch.where(targets == 1.0, self.alpha, 1.0 - self.alpha)
            else:
                # Multiclass Task: inputs are [E, num_classes], targets are [E] containing category indices
                targets = targets.to(device=current_device, dtype=torch.long).view(-1)

                # Stably calculate base Categorical Cross Entropy
                base_loss = functional.cross_entropy(
                    inputs, targets, reduction='none'
                )
                alpha_factor = 1.0

            # Compute pt directly from the stabilized log-space loss representation
            pt = torch.exp(-base_loss)

            # Calculate the focal weight with a safety clamp to protect backpropagation gradients
            focal_weight = alpha_factor * torch.pow(torch.clamp(1.0 - pt, min=1e-8), self.gamma)
            focal_loss = focal_weight * base_loss

            # Apply output structural reductions
            if self.reduction == 'mean':
                return focal_loss.mean()
            if self.reduction == 'sum':
                return focal_loss.sum()

            return focal_loss
