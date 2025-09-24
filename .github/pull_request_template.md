# Pull Request

## Summary

Explain what this PR changes and why.

## Change Type

- [ ] Feature
- [ ] Fix
- [ ] Refactor
- [ ] Docs
- [ ] Chore

## Related Issues

Closes #ISSUE_NUMBER (if applicable)

## Implementation Notes

Key decisions, data model changes, trade-offs.

## CDM / Seeder Impact

- [ ] CDM schema updated (model.json regeneration expected)
- [ ] Dataverse metadata (new entity/attribute/relationship)
- [ ] No persistence layer impact

## Validation Steps

Provide exact steps a reviewer can follow:

```bash
# Example
(dotnet build)
(dotnet run --project src/CdmBootstrapper)
```

## Screenshots / Outputs (Optional)

Before / after or diff excerpts.

## Copilot Assistance

Describe if Copilot helped (prompts, generated sections). If none, state: "None".

## Checklist

- [ ] Build passes locally (`dotnet build`)
- [ ] Intentional CDM changes committed (if any)
- [ ] Secrets NOT included
- [ ] Docs updated (README / CONTRIBUTING / comments)
- [ ] Added tests or noted absence with rationale
- [ ] PR title follows conventional style

## Risks & Mitigations

List potential issues and how addressed.
