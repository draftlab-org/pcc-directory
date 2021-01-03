<script>

    export let title;
    export let reader;
    export let number;

</script>

<li class="card__wrapper">
    <div class="card card--indicator">
        <header>
            <h3 class="card__number">
                <span class="card__link">{number}</span>
            </h3>
        </header>
        <div class="card__meta card__roles">
            <span class="screen-reader-text">{reader}: </span>
            <p class="card__role">
                {title}
            </p>
        </div>
    </div>
</li>
