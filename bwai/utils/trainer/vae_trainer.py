import torch
import torch.nn as nn
from .base_trainer import BaseTrainer


class VAE_Trainer(BaseTrainer):
    def __init__(self, model, optimer, fp16=False, **kwargs):
        self.model = model
        self.optimer = optimer
        self.fp16 = fp16
        self.scaler = torch.cuda.amp.GradScaler(enabled=fp16)

        super(VAE_Trainer, self).__init__(model=model, optimer=optimer, **kwargs)

    def train_step(self, packs):
        if len(packs) == 2:
            imgs, _ = packs
        elif len(packs) == 1:
            imgs = packs
        else:
            raise ValueError("The length of packs must be 1 or 2.")
        self.optimer.zero_grad()
        with torch.cuda.amp.autocast(enabled=self.fp16):
            packs = self.model(imgs)
            loss = self.model.loss_func(imgs, packs)
        self.scaler.scale(loss).backward()
        self.scaler.step(self.optimer)
        self.scaler.update()
        return {"Loss": "{:.2e}".format(loss.item())}
