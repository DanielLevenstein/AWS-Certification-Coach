# Model performance Optimization

Recommended Remediation Order
- Reconcile conflicting curated labels before changing model code.
- Add normalized AWS service aliases and semantic service-match features.
- Add concept-coverage features that are independent of full reference-answer overlap.
- Calibrate grade boundaries against curated examples rather than relying only on regression MSE.
- Revisit runtime exact-option and wrong-service guards so partial-credit expectations are represented consistently.