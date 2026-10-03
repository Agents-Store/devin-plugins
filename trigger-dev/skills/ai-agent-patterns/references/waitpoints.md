# Waitpoints (Human-in-the-Loop)

## In Tasks

```ts
import { task, wait } from "@trigger.dev/sdk";

export const approvalWorkflow = task({
  id: "approval-workflow",
  run: async (payload) => {
    const processed = await processData(payload);

    // Create the token first; its id starts with "waitpoint_".
    // Give token.id (or token.url / token.publicAccessToken) to the approver.
    const token = await wait.createToken({
      timeout: "24h",
      idempotencyKey: `approval-${payload.id}`,
    });
    await notifyApprover({ tokenId: token.id, url: token.url });

    // Wait for human approval — returns a Result object
    const result = await wait.forToken<{ approved: boolean; reason?: string }>(token.id);

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

// tokenId is the id returned by wait.createToken() (starts with "waitpoint_")
await wait.completeToken<{ approved: boolean }>(
  tokenId,
  { approved: true, reason: "Looks good" }
);
```

## Complete Token via REST API

```bash
curl -X POST "${TRIGGER_API_URL}/api/v1/waitpoints/tokens/${WAITPOINT_ID}/complete" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"data": {"approved": true, "reason": "Looks good"}}'
```

## Complete Token from React

```tsx
import { useWaitToken } from "@trigger.dev/react-hooks";

// tokenId = token.id and accessToken = token.publicAccessToken from wait.createToken()
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
The task resumes with an error if the token times out (default timeout `10m`) — handle gracefully.

### Self-hosted note
Waiting on a token does not checkpoint on self-hosted (checkpoints are a Cloud feature): the run stays `EXECUTING` and keeps its slot until the token is completed or times out.
