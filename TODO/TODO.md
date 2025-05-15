# Project TODOs

## GitHub Secret Automation

- **Status:** Planning
- **Priority:** High
- **Description:** Automate the population of GitHub Actions secrets after Terraform deployments.
- **Design Document:** [./Design/gh_secret_automation.md](./Design/gh_secret_automation.md)
- **Phases:**
  1.  [ ] **Update `terraform/outputs.tf`:** Add and verify all necessary outputs for GitHub secrets.
  2.  [ ] **Develop `scripts/gh_populate_secrets.sh`:** Create the new bash script to set secrets using `gh` CLI, Terraform outputs, and `.tfvars` files.
  3.  [ ] **Integrate `gh_populate_secrets.sh`:** Modify `scripts/gcp_apply.sh` to call the new secret population script upon successful completion.
  4.  [ ] **Test Automation:** Thoroughly test the secret automation on `develop` and `main` branches.
  5.  [ ] **Documentation:** Update `README.md` and `Design/Setup.md` to reflect the new automation, prerequisites (gh CLI), and distinguish between automated and manual secrets.

---
