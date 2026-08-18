# Waitpoints (Human-in-the-Loop)

## In Tasks

```ts
import { task, wait } from "@trigger.dev/sdk";

export const approvalWorkflow = task({
  id: "approval-workflow",
  run: async (payload) => {
    const processed = await processData(payload);

    // Wait for human approval — returns a Result object
    const result = await wait.forToken<{ approved: boolean; reason?: string }>(
      `approval-${payload.id}`
    );

    if (result.ok && result.output.approved) {
      return await finalizeData(processed);
    }

    throw new Error(`Rejected: ${result.ok ? result.output.reason : "timed out"}`);
  },
});
```

## Complete Token via SDK

```ts
import { wait } from "@trigger.dev/sdk";

await wait.completeToken<{ approved: boolean }>(
  `approval-${payload.id}`,
  { approved: true, reason: "Looks good" }
);
```

## Complete Token via REST API

```bash
curl -X POST "${TRIGGER_API_URL}/api/v1/waitpoints/tokens/${TOKEN_ID}/complete" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"data": {"approved": true, "reason": "Looks good"}}'
```

## Complete Token from React

```tsx
import { useWaitToken } from "@trigger.dev/react-hooks";

function ApprovalUI({ tokenId, accessToken }: Props) {
  const { complete } = useWaitToken(tokenId, { accessToken });

  return (
    <div>
      <button onClick={() => complete({ approved: true })}>Approve</button>
      <button onClick={() => complete({ approved: false, reason: "Needs revision" })}>
        Reject
      </button>
    </div>
  );
}
```

## Patterns

### Review Gate
Pause a pipeline for review before proceeding to a destructive action.

### Multi-Stage Approval
Chain multiple wait.forToken calls for multi-level sign-off.

### Timeout Handling
The task resumes with an error if the token times out — handle gracefully.
