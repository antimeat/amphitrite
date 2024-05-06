---
title: Transformer algorithm
---

The transform algorithm is fairly blunt instrument to say the least. Essentially we take an existing swell partition table and apply a window where we allow energy to penetrate unaffected by any refraction effects. The window is defined by two angles $\theta_1$ and $\theta_2$. For the remainder of the directions outside the window we assume a refraction effect. Here we define an angle $\theta_{split}$ that splits the two angles ($\theta_1$ and $\theta_2$), hence dividing the choice where incoming swells will be bent to either $\theta_1$ or $\theta_2$, depending which side of $\theta_{split}$ the incoming direction is. For the refraction formula where we have an incoming swell magnitude of $hs$ and direction of $\theta$ that is between $\theta_1$ and $\theta_{split}$, we apply the following: $\theta_{diff} = \theta_1 - \theta$, where if $\theta_1 - \theta \geqslant 80^o, => \theta_{diff} = 80^o$ and $hs_{bent} = \cos(\theta_{diff}) * hs$. For any given direction of $\theta$ in or outside the window we also apply a multiplication factor and attenuation factor where $hs_{final} = hs * multiplier$ and $period_{final} = period * attenuation$, where both $muliplier$ and $attenuation$ are between $[0,1]$. Finally, for $\theta$ between $\theta_1$ and $\theta_{split}$, $\theta_{bent} = \theta_1$. Similarly for $\theta$ between $\theta_2$ and $\theta_{split}$, $\theta_{bent} = \theta_2$

## Assumptions

-   maximum refraction amount of $\theta_{diff} = 80^o$, where $\cos(\theta_{diff}) \approx 0.1736$ and hence a maximum reduction of $hs * 0.1736$
-   $\theta_2 = 10^o$, $\theta_2$ clockwise of $\theta_1$, $\theta_1$ clockwise of $\theta_{split}$, $\theta_{split}$ clockwise of $\theta_2$

## Graphical representation

<div align="left">
    <img src="http://wa-vw-er/webapps/amphitrite/docs/transformer_algo.png" alt="Algorithm" width="95%"/>
</div>

## Reference cos table

<div align="left">
    <img src="http://wa-vw-er/webapps/amphitrite/docs/cos_table.png" alt="Algorithm" width="50%"/>
</div>

## Author

Daz Vink: daz.vink@bom.gov.au
