This files contains my current thinking of this project.

### Motivation
Haoyuan is paid to work on data-driven science at SLAC by Matthias.
Therefore, Haoyuan has to do something related to this.

The split-delay optics is quite complicated to align.
An auto-alignment without operator interference can make the alignment of the optics less prone to operator bias. 
It should be emphasized here that there is no guarantee of better performance with the auto-alignment procedure compared with operator.
Haoyuan's initial idea is just to fulfill the requirement of the funding source and to reduce the operator's bias.

## Targets
Because the optics is very complicated, Haoyuan considers it to be imporssible to achieve a complete auto-alignment from stretch during this development cycle.
Therefore, in the following, Haoyuan specifies a seires of target that he considers to be reasonable to achieve step by step.

### Target A
1. Create a window that constantly show the diode intensity for all diodes
2. Have a button for each crystal. By clicking on the button, perform a rocking curve scan of this crystal and move the crystal to the Bragg peak after the scan.

Why we need a button.

The reason that I believe that we need a button is because I do not want to give the one who runs this algorithm too much freedom. 
The reason that I do not want to make it more flexible is because I do not have the capability and capacity to guarantee robustness of the algorithm.
The robustness is however very important for the optics since there is usually no backup components for hard X-ray optics.
Damaging crystal is not acceptable.

### Target B
1. Create a button. After clicking on the button, bring one X-ray pulse to the other.

