---
title: Transformer
---

## Notes

-   Read the [algorithm](#algorithm) for details of how the Transformer works.
-   **Note:** site tables are defined in [Amphitrite](http://wa-vw-er/webapps/amphitrite/html/dashboard.php), not here. Hence the Transformer GUI does not allow you to change the backend spectral table that seeds the site you are _transforming_. To change the backend table, you need to re-configure Amphitrite.
-   Run tests via the Transformer GUI before editing the site configuration from the _edit-config_ menu. Running tests via the GUI does not save any output by default. You can, however, check the _save-output_ button to save the HTML output and CSV output, which then updates the HTML table output for that site and makes it available via HTML, as well as the _amphitrite_ data source in [Vulture](http://wa-vw-er/webapps/er_ml_projects/vulture/html/dashboard.php). Once a new model run arrives, the HTML output (_and amphitrite data source_) will be overridden using configuration in the site configuration.
-   Save site configurations you want to execute for each model run from the _edit-config_ menu.
-   Once you save the configuration from the _edit-config_ menu, the transformed data is available immediately on demand via HTML tables, amphitrite data source in Vulture, and in Ofcast. This configuration is executed with each new model run.
-   **Note:** use $\theta_{1} = 0$ and $\theta_{2} = 0$ in the Transformer GUI to return the original table without a transformation. This is useful for ground-truthing the original data that a site is transformed from.

## Algorithm

The transform algorithm is fairly blunt instrument to say the least. Essentially we take an existing swell partition table and apply a window where we allow energy to penetrate unaffected by any refraction effects. The window is defined by two angles $\theta_1$ and $\theta_2$. For the remainder of the directions outside the window we assume a refraction effect. Here we define an angle $\theta_{split}$ that splits the two angles ($\theta_1$ and $\theta_2$), hence dividing the choice where incoming swells will be bent to either $\theta_1$ or $\theta_2$, depending which side of $\theta_{split}$ the incoming direction is. For the refraction formula where we have an incoming swell magnitude of $hs$ and direction of $\theta$ that is between $\theta_1$ and $\theta_{split}$, we apply the following: $\theta_{diff} = \theta_1 - \theta$, where if $\theta_1 - \theta \geqslant 80^o, => \theta_{diff} = 80^o$ and $hs_{bent} = \cos(\theta_{diff}) * hs$. For any given direction of $\theta$ in or outside the window we also apply a multiplication factor and attenuation factor where $hs_{final} = hs * multiplier$ and $period_{final} = period * attenuation$, where both $muliplier$ and $attenuation$ are between $[0,1]$. Finally, for $\theta$ between $\theta_1$ and $\theta_{split}$, $\theta_{bent} = \theta_1$. Similarly for $\theta$ between $\theta_2$ and $\theta_{split}$, $\theta_{bent} = \theta_2$. As a result of initial verification as well as wave theory the multiplication factor has been broken down into two seperate factors, one for the short period partition and one for the longer period partitions. Hence we have defined multiplication factors to apply of $multi_{short}$ and $multi_{long}$. A final note, the multiplication factors are applied to every incoming direction, regardless of having the $\cos$ rule applied or not.

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
