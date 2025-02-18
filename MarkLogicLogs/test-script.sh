#!/bin/bash

# Get current time in seconds since epoch (UTC)
current_time=$(date -u +%s)

# Calculate timestamps for the last hour (3600 seconds)
start_time=$((current_time - 3600))

# Function to generate memory stats with slight variations
generate_memory_stats() {
    local rss=$((RANDOM % 1000 + 6000))
    local anon=$((RANDOM % 1000 + 5500))
    echo "Memory 42% phys=63610 size=27${rss}(43%) rss=${rss}(10%) huge=20480(32%) anon=${anon}(9%) file=449(0%) forest=4182(6%) cache=20480(32%) registry=1(0%)"
}

# Generate timestamps at 5-minute intervals
for i in {0..11}; do
    # Calculate timestamp for this iteration
    timestamp=$((start_time + (i * 300)))  # 300 seconds = 5 minutes
    
    # Convert to MarkLogic timestamp format (macOS compatible) in UTC
    formatted_time=$(date -u -j -f %s $timestamp "+%Y-%m-%d %H:%M:%S")
    base_time="$formatted_time"
    
    # Generate different types of log entries
    case $i in
        0)
            # Initial memory stats
            echo "$base_time.197 Info: Memory 42% phys=63610 size=27389(43%) rss=6491(10%) huge=20480(32%) anon=6114(9%) file=449(0%) forest=4181(6%) cache=20480(32%) registry=1(0%)"
            echo "$base_time.266 Info: Memory 42% phys=63610 size=27351(42%) rss=6494(10%) huge=20480(32%) anon=6076(9%) file=449(0%) forest=4182(6%) cache=20480(32%) registry=1(0%)"
            ;;
        1)
            # Memory and forest operations
            echo "$base_time.177 Info: Memory 42% phys=63610 size=27349(42%) rss=6456(10%) huge=20480(32%) anon=6074(9%) file=449(0%) forest=4182(6%) cache=20480(32%) registry=1(0%)"
            echo "$base_time.301 Info: Memory 41% phys=63610 size=27108(42%) rss=6213(9%) huge=20480(32%) anon=5833(9%) file=449(0%) forest=4182(6%) cache=20480(32%) registry=1(0%)"
            echo "$base_time.574 Info: Saving /var/opt/MarkLogic/Forests/Meters/00002148"
            echo "$base_time.707 Info: Saved 26 MB in 1 sec at 23 MB/sec to /var/opt/MarkLogic/Forests/Meters/00002148"
            echo "$base_time.744 Info: Merging 36 MB from /var/opt/MarkLogic/Forests/Meters/00002146 and /var/opt/MarkLogic/Forests/Meters/00002148 to /var/opt/MarkLogic/Forests/Meters/0000214a"
            echo "$base_time.813 Info: Merged 35 MB in 1 sec at 24 MB/sec to /var/opt/MarkLogic/Forests/Meters/0000214a"
            echo "$base_time.901 Info: Deleted 26 MB at 8140 MB/sec /var/opt/MarkLogic/Forests/Meters/00002146"
            echo "$base_time.904 Info: Deleted 26 MB at 8793 MB/sec /var/opt/MarkLogic/Forests/Meters/00002148"
            ;;
        2)
            # More memory stats
            echo "$base_time.364 Info: Memory 41% phys=63610 size=26863(42%) rss=5966(9%) huge=20480(32%) anon=5588(8%) file=448(0%) forest=4182(6%) cache=20480(32%) registry=1(0%)"
            echo "$base_time.347 Info: Memory 41% phys=63610 size=26883(42%) rss=5986(9%) huge=20480(32%) anon=5608(8%) file=448(0%) forest=4182(6%) cache=20480(32%) registry=1(0%)"
            ;;
        3)
            # WCO Forest operations
            echo "$base_time.611 Info: Saving /var/opt/data1/Forests/wco/000403b6"
            echo "$base_time.838 Info: Saved 15 MB at 66 MB/sec to /var/opt/data1/Forests/wco/000403b6"
            echo "$base_time.866 Info: Merging 21 MB from /var/opt/data1/Forests/wco/000403b6 and /var/opt/data1/Forests/wco/000403b5 to /var/opt/data1/Forests/wco/000403b7"
            echo "$base_time.883 Info: Merged 8 MB at 25 MB/sec to /var/opt/data1/Forests/wco/000403b7"
            echo "$base_time.929 Info: Deleted 8 MB at 1750 MB/sec /var/opt/data1/Forests/wco/000403b5"
            echo "$base_time.933 Info: Deleted 15 MB at 3669 MB/sec /var/opt/data1/Forests/wco/000403b6"
            ;;
        4)
            # Backup operations
            echo "$base_time.366 Notice: Finished backup of forest wco to s3://wc-test-data-backup/uat/wco/20250126-2200003696000, jobid=7884140171408662800"
            echo "$base_time.438 Notice+: Finishing backup of forest wco to s3://wc-test-data-backup/uat/wco/20250126-2200003696000/Forests/wco"
            echo "$base_time.483 Notice+: Finished backup of forest wco to s3://wc-test-data-backup/uat/wco/20250126-2200003696000/Forests/wco"
            echo "$base_time.483 Notice+: Finished 1-forest database backup to s3://wc-test-data-backup/uat/wco/20250126-2200003696000"
            ;;
        5)
            # Cleanup operations
            echo "$base_time.061 Info: Stopping data encryption of s3://wc-test-data-backup/uat/wco/20250124-2200003083220/Forests"
            echo "$base_time.523 Info: Deleted 184006 MB in 59 sec at 3104 MB/sec s3://wc-test-data-backup/uat/wco/20250119-2200003531760"
            ;;
        6|8|10)
            # Regular memory stats
            echo "$base_time.224 Info: Memory 41% phys=63610 size=27005(42%) rss=6108(9%) huge=20480(32%) anon=5729(9%) file=449(0%) forest=4182(6%) cache=20480(32%) registry=1(0%)"
            echo "$base_time.396 Info: Memory 42% phys=63610 size=27275(42%) rss=6383(10%) huge=20480(32%) anon=5999(9%) file=449(0%) forest=4182(6%) cache=20480(32%) registry=1(0%)"
            ;;
    esac
done


