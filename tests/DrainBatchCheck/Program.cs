// Regression check for PingGeneratorService.DrainBatch: draining a queue larger than the batch
// cap must move exactly `cap` items and leave the rest queued (the old loop silently lost one
// item per cycle). Exits 0 on success, 1 on failure.
using System.Collections.Concurrent;
using PingService.Models;
using PingService.Services;

// 1500 queued updates, numbered by latitude so order can be asserted.
var queue = new ConcurrentQueue<PingUpdate>();
for (var i = 0; i < 1500; i++) queue.Enqueue(new PingUpdate(i, i, 1));

var batch = new List<PingUpdate>();
var moved = PingGeneratorService.DrainBatch(queue, batch, 1000);
Console.WriteLine($"moved={moved} batch={batch.Count} left={queue.Count}");

// Exactly 1000 moved, 500 left, and the batch ends at item 999 (nothing skipped).
if (moved != 1000 || batch.Count != 1000 || queue.Count != 500 || batch[999].Latitude != 999)
{
    Console.WriteLine("FAIL: wrong batch size, remainder or contents");
    return 1;
}

// The first item still queued must be item 1000, i.e. no update was dropped at the boundary.
queue.TryDequeue(out var next);
if (next is null || next.Latitude != 1000)
{
    Console.WriteLine("FAIL: an update was lost at the batch boundary");
    return 1;
}

Console.WriteLine("PASS");
return 0;
