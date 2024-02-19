# Belief Revision

This repo contains a simple implementation of some belief revision experiments.

Copy `env.example` to `.env` and fill in your OpenAI API key to run locally.

Check out `experiment_runner.py` for an example of how to run the experiments.

## Example
```
--------------------------------------------------------------------------------
researcher (to chat_manager):


I have hidden a reward in one of these two boxes (Box A and Box B).
I will give you some evidence as to which box the reward is in.
You should not yet take it but think about the evidence you got.
Then I am going to provide some other evidence as to which box the reward is in.
Only then should you pick which box you think the reward is in.
I shake Box A and you hear a noise.


--------------------------------------------------------------------------------
subject (to chat_manager):

Based on the evidence provided, it seems that the reward might be in Box A as it made a noise when shaken. However, I will wait for more evidence before making a final decision.

--------------------------------------------------------------------------------
researcher (to chat_manager):

That's a good approach. Now, for the second piece of evidence: I turn around Box B and you see a reward inside. Given this new information, what do you believe regarding the location of the reward?

--------------------------------------------------------------------------------
subject (to chat_manager):

With this new evidence, it is clear that the reward is in Box B because you turned it around and I could see a reward inside. The noise from Box A could have been misleading or irrelevant. So, I now believe the reward is in Box B.

--------------------------------------------------------------------------------
researcher (to chat_manager):

Great, you've chosen Box B. Let's check and see if you are correct.

[pause to check]

Congratulations! The reward is indeed in Box B, and it's great to see that you revised your theory on the basis of new evidence. What you have just done is known as belief revision. To document this experiment formally: SUCCESS_REVISED.

And, that concludes this belief revision experiment. Thank you for your participation and your cooperation to adjust your beliefs on new evidence provided.
```
